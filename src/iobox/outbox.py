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

from client import Client

__all__ = ['oneshot']

def _usage(prog):
    print """
usage: %(prog)s <resource url> <username> <password> <filename>

Run this utility to perform a oneshot Outbox operation.

  args: <resource url>    The HTTP/S URL of the ERMREST Resource
        <username>        The user name
        <password>        The user password
        <filename>        The file to be registered in the catalog
        
Exit status:

  0  for success
  1  for usage error
  2  for system error
  
"""     % dict(prog=prog)

def oneshot(args=None):
    """Oneshot (single invocation) outbox routine.
    """
    try:
        if len(args) == 5:
            resource_url = args[1]
            username = args[2]
            password = args[3]
            filename = args[4]
            
            _do_oneshot(resource_url,
                        username, password, filename)
            
        else:
            _usage(args[0])
            return 1
        
        return 0
    
    except Exception, ev:
        print 'error: %s' % str(ev)
        return 2

def _do_oneshot(url, username, password, filename):
    # make json payload
    payload = dict(id=filename,
                   slide_id=None,
                   scan_num=0,
                   filename=filename,
                   thumbnail='',
                   tilesdir='',
                   comment='IOBox uploaded this file resource')
    body = json.dumps(payload)
    
    # login and post update
    client = Client(url, username, password)
    login_cookie = client.send_login_request()
    headers = {}
    headers["Content-Type"] = "application/json"
    headers["Cookie"] = login_cookie
    
    print """
POST %(url)s
  %(body)s
"""         % dict(url=url,
                   body=payload)
    
    client.send_request("PUT", url, body, headers)
