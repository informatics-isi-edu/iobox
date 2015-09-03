The `sql2bag` utility connects to a Relational DataBase Server, executes SQL selects, and makes a bag package. 

## Installation

### Prerequisites

1. Python 2.6 or higher
2. Python pyodbc
3. Python bagit
4. Python requests
5. ODBC connection 

### Installation on a Windows machine connecting to a local MS SQL Server data source

1. Create an ODBC Data Source  
  * Control Panel -> System and Security -> Administrative Tools -> Data Sources (ODBC)
  * Add an ODBC Driver Data Source
    * Enter a Name, Description and the name of the server. (You can give any name to the connection, but write it down as you will need the name 
      and server name later to connect to the data source)
  * Select the type of authentication you use to access your MS SQL database 
  * Test the connection in the connection Wizard 
2. Install the sql2dams tool from a 
  1. Install Python on your Windows system (it can be dowloaded from https://www.python.org/downloads/release/python-2710/ and follow installations defaults)
  2. Add C:\Python27 and C:\Python27\Scripts to the PATH environment variable
  3. Install additional Python libraries. Open a command window and type:
    * pip install pyodbc
    * pip install bagit
  4. Download the sql2bag.zip distribution file 
  5. Save the sql2bag.zip file to a location in your machine (e.g., C:\Users\myname\iobox) and unzip it
  6. Open a command window and cd to the folder of the unzipped code (e.g., C:\Users\myname\iobox\sql2bag-0.1-prerelease) and type the command
    * python setup.py install 
  7. Edit the sql2bag-config.json file found in the inputs folder to enter the Data Source values:
    *  "server_name":"mssql_server_name",
    *  "dns": "data_source1", (this is the name given to the connection in the odbc connection setup step above )
    *  "database_name":"my_db", (this is the name of the database in your ms sql server that you will be querying to extract data) 
    *  "user_name":"mssql_user_name", (this are the username and password you used to access your db based on the authentication method selected above)
    *  "db_password":"*********"
  8. Edit the sql2bag_inputs.js	file found in the inputs folder to enter the names and locations of the SQL query for the extracts files. sql2bag will 
     generate one CSV file for each extracts query file entered in the "extracts" blocl of the configuration file. The query file must contain 
     a query written in SQL.



From this directory, run:

`python setup.py install`



## Structure of the SQL2BAG configuration file:
The input to sql2bag.py is a configuration file in json. The structure of the configuration file is:

{
    "bag":
    {
      "bag_path":"./test_bag.zip"
    },
    "mssql_server":
    {
      "server_name":"SQL_SERVER_NAME",
      "dns": "MY_DATA_SOURCE",
      "database_name":"MY_DBNAME",
      "user_name":"MY_USER",
      "db_password":"*********"
    },
    "extracts": [
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

In the extracts block the "schema_name" is the directory under which the created CSV file will be placed in the created bag. 


