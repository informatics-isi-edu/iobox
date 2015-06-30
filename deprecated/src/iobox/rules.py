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
"""The rule processor and supporting class definitions."""

from models import RERule
import re


class RERuleProcessor(object):
    """Processes a rerule object into tags."""
    
    def __init__(self, rerule):
        """Constructor
        
        Keyword arguments:
        rerule -- rerule object
        
        """
        self._rerule = rerule
        self.prepattern_processor = None
        self.prepattern = None
        if self._rerule.prepattern is not None:
            self.prepattern_processor = RERuleProcessor(self._rerule.prepattern)
        self.pattern = re.compile(rerule.pattern)

        self.apply_func = dict(match=self.apply_match,
                          search=self.apply_search,
                          finditer=self.apply_finditer)[rerule.apply]

        self.tester_func = dict(match=re.match,
                           search=re.search,
                           finditer=re.search)[rerule.apply]

        self.extract_func = dict(constants=self.extract_constant,
                            single=self.extract_single, 
                            positional=self.extract_positional,
                            named=self.extract_named,
                            template=self.extract_template)[rerule.extract]

        self.rewrites = [ (re.compile(r.get_rewrite_pattern()), r.get_rewrite_template()) for r in rerule.rewrites ]

        self.constants = rerule.constants

        self.tags = rerule.tags

        self.templates = rerule.templates
        
    def test(self, string):
        if self.prepattern and not self.prepattern.test(string):
            return False
        if self.tester_func(self.pattern, string):
            return True
        else:
            return False

    def analyze(self, string):
        if self.prepattern_processor and not self.prepattern_processor.test(string):
            return dict()
        return self.apply_func(string)

    def rewrite(self, valuestring):
        for pattern, template in self.rewrites:
            valuestring = re.sub(pattern, template, valuestring)
        return valuestring

    def extract_constant(self, match):
        if match:
            return self.constants
        else:
            return dict()

    def extract_single(self, match):
        if match:
            return { self.tags[0].get_tag_name() : set([ self.rewrite(match.group(0)) ]) }
        else:
            return dict()

    def extract_positional(self, match):
        if match:
            return dict([ (self.tags[i], set( [self.rewrite(match.group(i+1))] )) for i in range(0, len(self.tags))
                          if self.tags[i] and self.rewrite(match.group(i+1)) ])
        else:
            return dict()

    def extract_named(self, match):
        if match:
            return dict([ (key, set([ self.rewrite(value) ]) ) for key, value in match.groupdict().items() if self.rewrite(value) ])
        else:
            return dict()

    def extract_template(self, match):
        if match:
            return dict([ (self.tags[i], set([self.rewrite(match.expand(self.templates[i]))]) ) for i in range(0, len(self.tags)) ])
        else:
            return dict()

    def apply_match(self, string):
        return self.extract_func( re.match(self.pattern, string) )

    def apply_search(self, string):
        return self.extract_func( re.search(self.pattern, string) )

    def apply_finditer(self, string):
        def dictmerge(tags, newtags):
            for tag, valset in newtags.items():
                if type(valset) != set:
                    if type(valset) == list:
                        valset = set(valset)
                    else:
                        valset = set([valset])
                if not tags.has_key(tag):
                    tags[tag] = valset.copy()
                else:
                    tags[tag].update(valset)

        tags = dict()
        for match in re.finditer(self.pattern, string):
            dictmerge(tags, self.extract_func(match))
        return tags


class PathRuleProcessor(RERuleProcessor):
    def analyze(self, file_path):
        return super(PathRuleProcessor, self).analyze(file_path)

