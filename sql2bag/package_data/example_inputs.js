{
    "SERVER_NAME":"bugacov.isi.edu",
    "DNS": "gpcr",
    "DATABASE_NAME":"rce",
    "USER_NAME":"sa",
    "CSV_TARGET_DIRECTORY":"data",
    "DESTINATION_SERVER_NAME":"vm-dev-029.misd.isi.edu",
    "EXTRACTS": [
         { "query_file" : "example_files/example_query_construct.sql",
	   "schema_name": "gpcr",
	   "table_name" : "construct",
	   "bulk_data_columns" : [],
	   "unique_key_columns": ["id"]
	 },
         { "query_file" : "example_files/example_query_cont_target.sql",
	   "schema_name": "gpcr",
	   "table_name" : "cont_target",
	   "bulk_data_columns" : [],
	   "unique_key_columns": ["id"]
	 },
         { "query_file" : "example_files/example_query_cont_target.sql",
	   "schema_name": "gpcr2",
	   "table_name" : "cont_target",
	   "bulk_data_columns" : [],
	   "unique_key_columns": ["id"]
	 }
    ]
}

