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
Models for Outbox configuration and local state.
"""

class Outbox(object):
    """Represents the Outbox configuration."""

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.state_db = kwargs.get("state_db")
        self.bulk_ops_max = kwargs.get("bulk_ops_max")
        self.url = kwargs.get("url")
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")
        self.goauthtoken = kwargs.get("goauthtoken")
        self.roots = kwargs.get("roots", [])
        self.includes = kwargs.get("includes", [])
        self.excludes = kwargs.get("excludes", [])
        self.path_rules = kwargs.get("path_rules", [])


class RERule(object):
    """A regular expression rule used for tagging."""
    
    def __init__(self, **kwargs):
        
        self.pattern = kwargs.get("pattern")
        self.apply = kwargs.get("apply", "match")
        self.extract = kwargs.get("extract", "single")
        self.rewrites = kwargs.get("rewrites", [])
        self.constants = kwargs.get("constants", [])
        


class RERuleConstant(object):
    """A constant assigned to a rerule."""
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.value = kwargs.get("value")        


class RERuleRewrite(object):
    """A rewrite pattern and template for a rerule."""
    def __init__(self, **kwargs):
        self.pattern = kwargs.get("pattern")
        self.template = kwargs.get("template")


class File(object):
    """Represents a File."""
    
    # File status flag values
    COMPUTE     = 0
    COMPARE     = 1
    REGISTER    = 2
    
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.filename = kwargs.get("filename")
        self.mtime = kwargs.get("mtime")
        self.rtime = kwargs.get("rtime")
        self.size = kwargs.get("size")
        self.checksum = kwargs.get("checksum")
        self.username = kwargs.get("username")
        self.groupname = kwargs.get("groupname")
        self.content_tags = kwargs.get("content_tags", [])
        self.status = kwargs.get("status")
        self.tags = kwargs.get("tags", [])
        
    def __str__(self):
        s = self.filename
        s += " <%s> " % self.id
        s += " (%s %s %s %s %s) [" % (self.mtime, self.rtime, self.size, 
                                      self.username, self.groupname)
        for t in self.tags:
            s += "%s, " % t
        s += "]"
        return s

