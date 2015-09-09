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
    
    if len(sys.argv) != 3:
        sys.stderr.write(""" 
usage: iobox_sql2dams.py <input_file.js> <temp_bag_folder>

<input_file.js>: reads input from <input_file.js> file. See below for format example. 
<temp_bag_folder>: local directory where extracted data will be teporarily saved before loading to DAMS 
 
input_file.js example:
{
    "SERVER_NAME":"mssql_server.isi.edu",
    "DNS": "gpcr",
    "DATABASE_NAME":"rce",
    "USER_NAME":"sa",
    "DB_PASSWORD":"********",
    "DESTINATION_SERVER_NAME":"vm-dev-029.misd.isi.edu",
    "DESTINATION_USER_NAME":"gpcr1",
    "DESTINATION_PASSWORD":"*******",
    "EXTRACTS": [
        { "query_file" : "gpcr_example/Status.sql",
           "schema_name": "gpcr_new",
           "table_name" : "Status",
           "bulk_data_columns" : [],
           "unique_key_columns": ["id"]
         },
         { "query_file" : "gpcr_example/Strain.sql",
           "schema_name": "gpcr_new",
           "table_name" : "Strain",
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

    bag_tmp=sys.argv[2]
    bag = sql2bag.create_bag(inputs_js,bag_tmp) 
    bag2dams.load_bag_csv(sys.argv[1],bag_tmp)

