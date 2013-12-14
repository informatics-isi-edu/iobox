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

import json
from httplib import HTTPException

from client import Client

__all__ = ['oneshot']

__OPT_USERNAME = '--username='
__OPT_PASSWORD = '--password='
__OPT_GOAUTH   = '--goauth'

def _usage(prog):
    print """
usage: %(prog)s [OPTIONS] <resource url> {<key>=<value>+}

Run this utility to perform a oneshot Outbox operation.

  options:
      --username=<username>    The user name.
      --password=<password>    The user password.
      --goauth                 Use Globus authentication.

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
    # parse options
    options = [opt for opt in args if opt.startswith('--')]
    for opt in options:
        if opt.startswith(__OPT_USERNAME):
            username = opt[len(__OPT_USERNAME):]
        elif opt.startswith(__OPT_PASSWORD):
            password = opt[len(__OPT_PASSWORD):]
        elif opt.startswith(__OPT_GOAUTH):
            goauth = True
        else:
            _usage(args[0])
            return 1
    
    # parse required args
    args = [arg for arg in args if arg not in options]
    if len(args) < 3:
        _usage(args[0])
        return 1
    resource_url = args[1]
    body = dict()
    for keyval in args[2:]:
        (key, value) = keyval.split('=',1)
        body[key] = value
        
    try:
        print str(body)
        _do_oneshot(resource_url, username, password, body)
        print "successfully imported: " % str(body)
        return 0
    
    except HTTPException, ev:
        print str(ev)
        return 2
    
    except Exception, ev:
        print 'error: %s' % str(ev)
        return 3

def _do_oneshot(url, username, password, body):
    # make json payload
    body = json.dumps([body])
    
    # login and post update
    client = Client(url, username, password)
    login_cookie = client.send_login_request()
    headers = {}
    headers['Content-Type'] = 'application/json'
    headers['Cookie'] = login_cookie
    path = client.path
    
    # send update
    return client.send_request('PUT', path, body, headers)
