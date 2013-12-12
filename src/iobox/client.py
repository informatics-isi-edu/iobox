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
Raw network client for HTTP(S) communication with ERMREST service.
"""

import urlparse
from httplib import HTTPConnection, HTTPSConnection, HTTPException, OK, CREATED, ACCEPTED, NO_CONTENT


class Client (object):
    """Network client for ERMREST.
    """
    ## Derived from the tagfiler iobox service client

    def __init__(self, baseuri, username, password):
        self.baseuri = baseuri
        o = urlparse.urlparse(self.baseuri)
        self.scheme = o[0]
        host_port = o[1].split(":")
        self.host = host_port[0]
        self.path = o.path
        self.port = None
        if len(host_port) > 1:
            self.port = host_port[1]
        self.username = username
        self.password = password

    def send_request(self, method, url, body='', headers={}):
        
        webconn = None
        if self.scheme == 'https':
            webconn = HTTPSConnection(host=self.host, port=self.port)
        elif self.scheme == 'http':
            webconn = HTTPConnection(host=self.host, port=self.port)
        else:
            raise ValueError('Scheme %s is not supported.' % self.scheme)
        webconn.request(method, url, body, headers)
        resp = webconn.getresponse()
        if resp.status not in [OK, CREATED, ACCEPTED, NO_CONTENT]:
            raise HTTPException("Error response (%i) received: %s" % (resp.status, resp.read()))
        return resp

    def send_login_request(self):
        headers = {}
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        resp = self.send_request("POST", "/ermrest/authn/session", "username=%s&password=%s" % (self.username, self.password), headers)
        return resp.getheader("set-cookie")
