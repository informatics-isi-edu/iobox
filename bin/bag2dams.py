#!/usr/bin/env python                                                                                                                                                            
#                                                                                                                                                                                
# Copyright 2015 University of Southern California                                                                                                                               
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

import sys
from iobox.bag2dams import bag2dams


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("""
usage: python bag2dams.py <config_file>
where <config_file> is the full path to the JSON file containing the configuration that will be used to upload
entities and assets to the DAMS. Authentication can be either via session username and password or via
passing a value of a valid ermrest (browser) cookie for goauth authentication. If username and password values are
passed it assumes local session authentication. If username and password are empty and cookie value is not empty
then it uses the passed value to construct a valid cookie. \n
""")
        sys.exit(1)

    try:
        bag2dams.import_from_bag(argv[1])
        sys.exit(0)
    except Exception as e:
        print e
        sys.exit(1)

if __name__ == '__main__':
    main(sys.argv)
