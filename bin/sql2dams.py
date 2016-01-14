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
import json
import iobox
from iobox.sql2bag import sql2bag
from iobox.bag2dams import bag2dams

if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        sys.stderr.write(""" 
usage: iobox_sql2dams.py <input_file.js> 

<input_file.js>: reads input from <input_file.js> file. See below for format example. 
 
input_file.js example:

{
    "bag":
    {
        "bag_path":"gpcr_bag"
    },
    "mssql_server":
    {
        "server_name":"bugacov.isi.edu",
        "dns": "gpcr_test",
        "database_name":"rce",
        "user_name":"sa",
        "db_password":"*********"
    },
    "catalog":
    {
        "host": "https://gpcr-dev.misd.isi.edu",
	"path": "/ermrest/catalog/1",
	"username": "",
	"password": "",
        "cookie_value": "*****************",
        "entities":
        [
         { "input_path": "iobox_data/targetlist.csv",
           "entity_path": "/entity/iobox_data:targetlist",
           "input_format": "csv"
         },
         { "input_path": "iobox_data/cleavagesite.sql",
	   "entity_path": "/entity/iobox_data:cleavagesite",
	   "input_format": "csv"
	 }
    },
    "extracts": [
         { "query_file" : "gpcr_iobox/targetlist.sql",
	   "schema_name": "iobox_data",
	   "table_name" : "targetlist",
	   "bulk_data_columns" : [],
	   "unique_key_columns": ["id"]
	 },
         { "query_file" : "gpcr_iobox/cleavagesite.sql",
	   "schema_name": "iobox_data",
	   "table_name" : "cleavagesite",
	   "bulk_data_columns" : [],
	   "unique_key_columns": ["id"]
	 }
    ]
}

1) DNS is the Data Source Name used in the ODBC connector. 
2) Each query_file must contain a properly writen query in SQL.

""")
        sys.exit(1)

    inputs_js= json.loads(open(sys.argv[1]).read())
    bag = sql2bag.create_bag(inputs_js) 
    bag2dams.import_from_bag(sys.argv[1])
    sys.exit(0)
