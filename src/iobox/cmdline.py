# 
# Copyright 2014 University of Southern California
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Command-line interface for the Ermrest Outbox.
"""

import version
from models import File, RERule, Outbox
from dao import OutboxStateDAO
from files import tree_scan_stats, create_uri_friendly_file_path, sha256sum
from client import ErmrestClient, UnresolvedAddress, NetworkError, ProtocolError, MalformedURL

import os
import sys
import logging
import argparse
import json
import socket
import re
import time

logger = logging.getLogger(__name__)

# Exit return codes
__EXIT_SUCCESS = 0
__EXIT_FAILURE = 1

# Used by ArgumentParser
__PROG = "ermrest-outbox"
__DESC = "The Ermrest Outbox command-line utility."
__VER  = "%(prog)s " + ("%d.%d trunk" % (version.MAJOR, version.MINOR))
__DEFAULT_OUTBOX_NAME = "outbox"
__BULK_OPS_MAX = 1000

# Verbosity to Loglevel dictionary
__LOGLEVEL = {0: logging.ERROR,
              1: logging.WARNING,
              2: logging.INFO,
              3: logging.DEBUG}
__LOGLEVEL_MAX = 3
__LOGLEVEL_DEFAULT = 3


def main(args=None):
    """
    The main routine.
    
    Optionally accepts 'args' but this is more of a convenience for unit 
    testing this module. It passes 'args' directly to the ArgumentParser's
    parse_args(...) method.
    """
    parser = argparse.ArgumentParser(prog=__PROG, description=__DESC)

    # General options
    parser.add_argument('--version', action='version', version=__VER)
    
    # Outbox name
    helpstr=('name of the outbox configuration (default: %s)' % 
             __DEFAULT_OUTBOX_NAME)
    parser.add_argument('-n', '--name', type=str, help=helpstr)
    
    # Use home directory as default location for outbox.conf
    default_config_filename = os.path.join(
            os.path.expanduser('~'), '.ermrest', 'outbox.conf')
    parser.add_argument('-f', '--filename', type=str, 
                        help=('configuration filename (default: %s)' % 
                              default_config_filename))
    
    # Use home directory as default location for state.db
    default_state_db = os.path.join(os.path.expanduser('~'), 
                                    '.ermrest', 'state.db')
    parser.add_argument('-s', '--state_db', type=str, 
                        help=('local state database (default: %s)' % 
                              default_state_db))
    
    # Verbose | Quite option group
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='count', 
                       default=__LOGLEVEL_DEFAULT, 
                       help='verbose output (repeat to increase verbosity)')
    group.add_argument('-q', '--quiet', action='store_true', 
                       help='suppress output')
    
    # Directory and Inclusion/Exclusion option group
    group = parser.add_argument_group(title='Directory traversal options')
    group.add_argument('--root', metavar='DIRECTORY', 
                       type=str, nargs='+',
                       help='root directories to be traversed recursively')
    group.add_argument('--exclude', type=str, nargs='+',
                       help='exclude based on regular expression')
    group.add_argument('--include', type=str, nargs='+',
                       help='include based on regular expression')
    
    # Ermrest option group
    group = parser.add_argument_group(title='Ermrest options')
    group.add_argument('--username', dest='username', metavar='USERNAME', 
                       type=str, help='username for your Tagfiler user account')
    group.add_argument('--password', dest='password', metavar='PASSWORD', 
                       type=str, help='password for your Tagfiler user account')
    group.add_argument('--url', dest='url', metavar='URL', 
                       type=str, help='URL of the Ermrest service')
    group.add_argument('--goauthtoken', dest='goauthtoken', metavar='GOAUTHTOKEN', 
                       type=str, help='GOAuth token from GO authentication')
    group.add_argument('--bulk_ops_max', type=int, 
                        help='maximum bulk operations per call to Tagfiler' + \
                        ' (default: %d)' % __BULK_OPS_MAX)
    
    # Now parse them
    args = parser.parse_args(args)
    
    # Turn verbosity into a loglevel setting for the global logger
    if args.quiet:
        logging.getLogger().addHandler(logging.NullHandler())
        # Should probably suppress stderr and stdout
    else:
        verbosity = args.verbose if args.verbose < __LOGLEVEL_MAX else __LOGLEVEL_MAX
        logging.basicConfig(level=__LOGLEVEL[verbosity])
        logger.debug("args: %s" % args)
    
    # Load configuration file, or create configuration based on arguments
    filename = args.filename or default_config_filename
    cfg = {}
    if os.path.exists(filename):
        f = open(filename, 'r')
        try:
            cfg = json.load(f)
            logger.debug("config: %s" % cfg)
        except ValueError as e:
            print >> sys.stderr, ('ERROR: Malformed configuration file: %s' % e)
            return __EXIT_FAILURE
        else:
            f.close()
    
    # Create outbox model, and populate from settings
    outbox_model = Outbox()
    outbox_model.name = args.name or cfg.get('name', __DEFAULT_OUTBOX_NAME)
    outbox_model.state_db = args.state_db or \
                            cfg.get('state_db', default_state_db)

    # Ermrest settings
    outbox_model.url = args.url or cfg.get('url')
    if not outbox_model.url:
        parser.error('Ermrest URL must be given.')
    
    outbox_model.username = args.username
    outbox_model.password = args.password
    outbox_model.goauthtoken = args.goauthtoken or cfg.get('goauthtoken')
    if not outbox_model.goauthtoken and \
        (not outbox_model.username or not outbox_model.password):
        parser.error('Ermrest username and password must be given.')
    outbox_model.bulk_ops_max = args.bulk_ops_max or \
                                cfg.get('bulk_ops_max', __BULK_OPS_MAX)
    outbox_model.bulk_ops_max = int(outbox_model.bulk_ops_max)
        
    
    # Roots
    roots = args.root or cfg.get('roots')
    if not roots or not len(roots):
        parser.error('At least one root directory must be given.')
    for root in roots:
        outbox_model.roots.append(root)
    
    # Add include/exclusion patterns
    excludes = args.exclude or cfg.get('excludes')
    if excludes and len(excludes):
        for exclude in excludes:
            outbox_model.excludes.append(re.compile(exclude))
    
    includes = args.include or cfg.get('includes')
    if includes and len(includes):
        for include in includes:
            outbox_model.includes.append(re.compile(include))
    
    # Establish Ermrest client connection
    try:
        client = ErmrestClient(outbox_model.url, outbox_model.username, 
                            outbox_model.password, outbox_model.goauthtoken)
        client.connect()
    except MalformedURL as err:
        print >> sys.stderr, ('ERROR: %s' % err)
        return __EXIT_FAILURE
    except UnresolvedAddress as err:
        print >> sys.stderr, ('ERROR: %s' % err)
        return __EXIT_FAILURE
    except NetworkError as err:
        print >> sys.stderr, ('ERROR: %s' % err)
        return __EXIT_FAILURE
    except ProtocolError as err:
        print >> sys.stderr, ('ERROR: %s' % err)
        return __EXIT_FAILURE
    
    state = OutboxStateDAO(outbox_model.state_db)
    worklist = []
    rworklist = []
    found = 0
    skipped = 0
    registered = 0
    added = 0

    # walk the root trees, cksum as needed, create worklist to be registered
    for root in outbox_model.roots:
        for (rfpath, size, mtime, user, group) in \
                tree_scan_stats(root, outbox_model.excludes, outbox_model.includes):
            filename = create_uri_friendly_file_path(root, rfpath)
            fargs = {'filename': filename, 'mtime': mtime, 'size': size, \
                    'username': user, 'groupname': group}
            f = File(**fargs)
            found += 1
            
            # Check if file exists in local state db
            exists = state.find_file(filename)
            if not exists:
                # Case: New file, not seen before
                logger.debug("New: %s" % filename)
                f.checksum = sha256sum(filename)
                state.add_file(f)
                worklist.append(f)
                rworklist.append(f)
                added += 1
            elif not exists.rtime:
                # Case: File has not been registered
                logger.debug("Not registered: %s" % filename)
                rworklist.append(exists)
            else:
                # Case: File does not meet any criteria for processing
                logger.debug("Skipping: %s" % filename)
                skipped += 1
    
    # Register files in worklist
    if len(worklist):
        client.add_subjects(worklist, outbox_model.bulk_ops_max)
    for f in rworklist:
        logger.debug("Registered: %s" % f.filename)
        f.rtime = time.time()
        state.update_file(f)
        registered += 1
    
    # Print final message unless '--quiet'
    if not args.quiet:
        # Print concluding message to stdout
        print "Done. Found=%s Added=%s Skipped=%s Registered=%s" % \
                    (found, added, skipped, registered)
    
    try:
        client.close()
    except NetworkError as err:
        print >> sys.stderr, ('WARN: %s' % err)
    return __EXIT_SUCCESS
