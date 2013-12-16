#!/usr/bin/env python
# 
# Copyright 2010 University of Southern California
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
Command line routines for the Outbox
"""

import os
import getpass
import json
import httplib

from client import Client

__all__ = ['oneshot']

__OPT_HELP       = '--help'
__OPT_USERNAME   = '--username='
__OPT_PASSWORD   = '--password='
__OPT_GOAUTH_URL = '--goauth-url='
__OPT_GOAUTH_TOK = '--goauth-tok='
__GOAUTH_TEST_IDP    = 'https://graph.api.test.globuscs.info/goauth/token?grant_type=client_credentials'
__GOAUTH_SERBAN_IDP  = 'https://serbancentos.isi.edu/goauth/token?grant_type=client_credentials'
__GOAUTH_DEFAULT_IDP = __GOAUTH_TEST_IDP


def _usage(prog):
    print """
usage: %(prog)s [OPTIONS] <resource url> {<key>=<value>+}

Run this utility to perform a oneshot Outbox operation.

  options:
      --help                   Print this and exit.
      --username=<username>    The user name.
      --password=<password>    The user password.
      --goauth-url=<url>       Use the goauth identity provider at <url>.
      --goauth-tok=[@<file>|<token>]
                               Use the goauth token presented directly in
                               <token> or read from <file>.

  arguments:
      <resource url>           The resource (entity) URL.
      <key>=<value>+           One or more key=value pairs to assign to the
                               resource.

Exit status:

  0  for success
  1  for usage error
  2  for server error
  3  for system error
  
"""     % dict(prog=prog)


def oneshot(args=None):
    """Oneshot (single invocation) outbox routine.
    """
    prog = os.path.basename(args[0])
    # parse options
    username, password = (None, None)
    goauthurl, goauthtok = (None, None)
    options = [opt for opt in args if opt.startswith('--')]
    for opt in options:
        if opt == __OPT_HELP:
            _usage(prog)
            return 0
        elif opt.startswith(__OPT_USERNAME):
            username = opt[len(__OPT_USERNAME):]
        elif opt.startswith(__OPT_PASSWORD):
            password = opt[len(__OPT_PASSWORD):]
        elif opt.startswith(__OPT_GOAUTH_URL):
            goauthurl = opt[len(__OPT_GOAUTH_URL):]
            goauthurl = goauthurl if len(goauthurl)>0 else __GOAUTH_DEFAULT_IDP
        elif opt.startswith(__OPT_GOAUTH_TOK):
            goauthtok = opt[len(__OPT_GOAUTH_TOK):]
            if goauthtok.startswith('@'):
                f = file(goauthtok[1:])
                goauthtok = f.read()
        else:
            _usage(prog)
            return 1
    
    # parse required args
    args = [arg for arg in args if arg not in options]
    if len(args) < 3:
        _usage(prog)
        return 1
    resource_url = args[1]
    body = dict()
    for keyval in args[2:]:
        (key, value) = keyval.split('=',1)
        body[key] = value
    
    # check if password needed
    if not goauthtok:
        if not username:
            print "error: goauth-tok or username and password required"
            return 1
        elif not password:
            password = getpass.getpass('password:')
    
    try:
        if goauthtok:
            _do_oneshot(resource_url, body,
                        goauthtok=goauthtok)
        else:
            _do_oneshot(resource_url, body,
                        username=username,
                        password=password,
                        goauthurl=goauthurl)
    
    except httplib.HTTPException, ev:
        print 'error: %s' % str(ev)
        return 2
    
    except Exception, ev:
        print 'error: %s' % str(ev)
        return 3
    
    print "successfully imported: " + str(body)
    return 0


def _do_oneshot(url, body, **kwargs):
    client = Client(url)
    path = client.path
    headers = {'Content-Type': 'application/json'}
    body = json.dumps([body])
    
    if 'goauthtok' in kwargs:
        headers['Globus-Goauthtoken'] = kwargs['goauthtok']
        #print "using goauth token: " + str(headers)
    else:
        login_cookie = client.send_login_request(kwargs['username'], kwargs['password'])
        headers['Cookie'] = login_cookie
        
    # send update
    return client.send_request('PUT', path, body, headers)