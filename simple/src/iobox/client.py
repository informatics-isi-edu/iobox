#!/usr/bin/env python
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
Raw network client for HTTP(S) communication with ERMREST service.
"""

import json
import base64
import urlparse
from httplib import HTTPConnection, HTTPSConnection, HTTPException, OK, CREATED, ACCEPTED, NO_CONTENT
import logging
import os
import urllib

logger = logging.getLogger(__name__)

class ErmrestException(Exception):
    def __init__(self, value, cause=None):
        super(ErmrestException, self).__init__(value)
        self.value = value
        self.cause = cause
        
    def __str__(self):
        message = "%s." % self.value
        if self.cause:
            message += " Caused by: %s." % self.cause
        return message

class MalformedURL(ErmrestException):
    """MalformedURL indicates a malformed URL.
    """
    def __init__(self, cause=None):
        super(MalformedURL, self).__init__("URL was malformed", cause)

class UnresolvedAddress(ErmrestException):
    """UnresolvedAddress indicates a failure to resolve the network address of
    the Ermrest service.
    
    This error is raised when a low-level socket.gaierror is caught.
    """
    def __init__(self, cause=None):
        super(UnresolvedAddress, self).__init__("Could not resolve address of host", cause)

class NetworkError(ErmrestException):
    """NetworkError wraps a socket.error exception.
    
    This error is raised when a low-level socket.error is caught.
    """
    def __init__(self, cause=None):
        super(NetworkError, self).__init__("Network I/O failure", cause)

class ProtocolError(ErmrestException):
    """ProtocolError indicates a protocol-level failure.
    
    In other words, you may have tried to add a tag for which no tagdef exists.
    """
    def __init__(self, message='Network protocol failure', errorno=-1, response=None, cause=None):
        super(ProtocolError, self).__init__("Ermrest protocol failure", cause)
        self._errorno = errorno
        self._response = response
        
    def __str__(self):
        message = "%s." % self.value
        if self._errorno >= 0:
            message += " HTTP ERROR %d: %s" % (self._errorno, self._response)
        return message
    
class NotFoundError(ErmrestException):
    """Raised for HTTP NOT_FOUND (i.e., ERROR 404) responses."""
    pass


class Client (object):
    """Network client for ERMREST.
    """
    ## Derived from the ermrest iobox service client

    def __init__(self, baseuri, use_goauth=False):
        self.baseuri = baseuri
        o = urlparse.urlparse(self.baseuri)
        self.scheme = o[0]
        host_port = o[1].split(":")
        self.host = host_port[0]
        self.path = o.path
        self.port = None
        if len(host_port) > 1:
            self.port = host_port[1]
        self.use_goauth = use_goauth

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

    def send_login_request(self, username, password):
        if self.use_goauth:
            auth = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
            headers = dict(Authorization='Basic %s' % auth)
            resp = self.send_request('GET', '/service/nexus/goauth/token?grant_type=client_credentials', '', headers)
            goauth = json.loads(resp.read())
            access_token = goauth['access_token']
            return dict(Authorization='Globus-Goauthtoken %s' % access_token)
        else:
            headers = {}
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            resp = self.send_request("POST", "/ermrest/authn/session", "username=%s&password=%s" % (username, password), headers)
            return dict(Cookie=resp.getheader("set-cookie"))

class ErmrestClient (object):
    """Network client for ERMREST.
    """
    ## Derived from the ermrest iobox service client

    def __init__(self, baseuri, username, password, use_goauth=False):
        self.baseuri = baseuri
        o = urlparse.urlparse(self.baseuri)
        self.scheme = o[0]
        host_port = o[1].split(":")
        self.host = host_port[0]
        self.path = o.path
        self.port = None
        if len(host_port) > 1:
            self.port = host_port[1]
        self.use_goauth = use_goauth
        self.username = username
        self.password = password
        self.header = None
        self.webconn = None

    def send_request(self, method, url, body='', headers={}):
        if self.header:
            headers.update(self.header)
        self.webconn.request(method, url, body, headers)
        resp = self.webconn.getresponse()
        if resp.status not in [OK, CREATED, ACCEPTED, NO_CONTENT]:
            raise HTTPException("Error response (%i) received: %s" % (resp.status, resp.read()))
        return resp

    def connect(self):
        if self.scheme == 'https':
            self.webconn = HTTPSConnection(host=self.host, port=self.port)
        elif self.scheme == 'http':
            self.webconn = HTTPConnection(host=self.host, port=self.port)
        else:
            raise ValueError('Scheme %s is not supported.' % self.scheme)

        if self.use_goauth:
            auth = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
            headers = dict(Authorization='Basic %s' % auth)
            resp = self.send_request('GET', '/service/nexus/goauth/token?grant_type=client_credentials', '', headers)
            goauth = json.loads(resp.read())
            access_token = goauth['access_token']
            self.header = dict(Authorization='Globus-Goauthtoken %s' % access_token)
        else:
            headers = {}
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            resp = self.send_request("POST", "/ermrest/authn/session", "username=%s&password=%s" % (self.username, self.password), headers)
            self.header = dict(Cookie=resp.getheader("set-cookie"))
        
    def add_subjects(self, fileobjs, bulk_ops_max):
        """Registers a list of files in ermrest using a single request.
        
        Keyword arguments:
        
        fileobjs -- the list of register files objects 
        
        """
        
        chunks = len(fileobjs) / bulk_ops_max + 1
        slides = {}
        for i in range(0, chunks):
            start = i * bulk_ops_max
            files = fileobjs[start:start+bulk_ops_max]
            body = []
            for f in files:
                slide_id = os.path.basename(os.path.dirname(f.filename))
                if slide_id not in slides:
                    url = '%s/attribute/scan/slide_id=%s/scan_num' % (self.path, urllib.quote(slide_id, safe=''))
                    headers = {'Content-Type': 'application/json',
                               'Accept': 'application/json'}
                    resp = self.send_request('GET', url, '', headers)
                    resp = json.loads(resp.read())
                    num = 0;
                    for val in resp:
                        if val['scan_num'] > num:
                            num = val['scan_num']
                    slides[slide_id] = num
                slides[slide_id] += 1
                num = slides[slide_id]
                obj = self.getScanAttributes(f,slide_id,num)
                body.append(obj)
            url = '%s/entity/scan' % self.path
            headers = {'Content-Type': 'application/json'}
            try:
                self.send_request('PUT', url, json.dumps(body), headers)
            except HTTPException, e:
                logger.error('Error during PUT attempt:\n%s' % str(e))
            except:
                raise
                    
        
    def getScanAttributes(self, f, slide_id, num):
        obj = {}
        suffix = '000%d' % num
        obj['id'] = '%s-%s' % (slide_id, suffix[-3:])
        obj['slide_id'] = slide_id
        obj['scan_num'] = num
        obj['filename'] = os.path.basename(f.filename)
        return obj
    
    def close(self):
        """Closes the connection to the Ermrest service.
        
        The underlying python documentation is not very helpful but it would
        appear that the HTTP[S]Connection.close() could raise a socket.error.
        Thus, this method potentially raises a 'NetworkError'.
        """
        assert self.webconn
        try:
            self.webconn.close()
        except socket.error as e:
            raise NetworkError(e)
        finally:
            self.webconn = None
