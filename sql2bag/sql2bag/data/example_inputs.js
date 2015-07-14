{
    "SERVER_NAME":"bugacov.isi.edu",
    "DNS": "gpcr",
    "DATABASE_NAME":"rce",
    "USER_NAME":"sa",
    "DB_PASSWORD":"*********",
    "DESTINATION_SERVER_NAME":"vm-dev-029.misd.isi.edu",
    "DESTINATION_USER_NAME":"gpcr1",
    "DESTINATION_PASSWORD":"********",
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

