#!/usr/bin/python

import os
import pyodbc
import csv
import sys
import datetime
import json
import shutil 
import bagit

from dams2bag.dams2bag import archive_bag
from dams2bag.dams2bag import cleanup_bag



py_dic = { str: 'str', buffer: 'buffer', int: 'int', float: 'float', datetime.datetime: 'datetime.datetime',
           datetime.date: 'datetime.date',datetime.time: 'datetime.time', bool: 'bool', 
           unicode: 'unicode', bytearray: 'bytearray' , long: 'long' }


PATH_SEP=os.path.sep


def read_query(query_file):
    with open(query_file) as sqlfile:
        sql_query=sqlfile.read()
        return sql_query

def read_json(input_file):
    json_input=open(input_file).read()
    return json.loads(json_input)


def val2text(v):
    if v is None:
        return ''
    elif type(v) == datetime.datetime:
        return v.isoformat()
    elif type(v) == datetime.date:
        return v.isoformat()
    elif type(v) in [int, float, str]:
        return '%s' % str(v)
    elif type(v) == unicode:
        return v.encode("utf-8")
    elif type(v) == buffer:
        try:
            return '{%s}' % uuid.UUID(bytes_le=v)
        except:
            return '\\x%s' % str(v).encode('hex')
    elif type(v) in [bool]:
        return '%s' % str(v)
    else:
        raise TypeError('value of type %s not supported yet' % type(v))

def csvescape(v):
    if v == None:
        return ''
    elif type(v) in [int, float]:
        return "%s" % v
    else:
        try:
            v = v.replace( '"', '""' )
            v = v.replace( '\n', '' )
            v = v.replace( '\r', '' )
            v = v.replace( '\00', '' )
        except:
            print 'type: %s v: %s' % (type(v), v)
            raise
        #return ''.join([ '"', v.encode("utf-8"), '"' ])       
        return v.encode("utf-8")       


def write_csv(cursor,csv_file):
    header = []
    for colinfo in cursor.description:
        colname = colinfo[0]
        header.append(colname.lower())

    if not os.path.exists(os.path.dirname(csv_file)):
        os.makedirs(os.path.dirname(csv_file))

    with open(csv_file,'wb') as f:
        writer = csv.writer(f)
        writer.writerow(header)

    for row in cursor:
        values = []
        for i in range(0, len(row)):
            values.append(val2text(row[i]).encode("utf-8"))
        with open(csv_file,'ab') as f:
            writer = csv.writer(f)
            writer.writerow(values)


def write_manifest(inputs_js,col_defs):

    manifest={}
    extracts =[]
    for ee in inputs_js['extracts']:
        extract={}
        extract['table_data']=csv_filename(ee)
        extract['schema_name']=ee['schema_name']
        extract['table_name']=ee['table_name']
        extract['column_definitions']=col_defs[csv_filename(ee)]
        extract['object_columns']=ee['bulk_data_columns']
        extract['unique_key_columns']=ee['unique_key_columns']        
        extracts.append(extract)

    manifest['extracts']=extracts
    source={}
    source['source_server_name']=inputs_js['mssql_server']['server_name']
    source['source_db_name']=inputs_js['mssql_server']['database_name']
    source['source_dns']=inputs_js['mssql_server']['dns']
    manifest['sql_source']=source


    return manifest


def write_schema(inputs_js,col_defs):


    schemas={}
    schemas_vect=[]
    
    schema_names={}
    for ee in inputs_js['extracts']:
        if ee['schema_name'] not in schema_names.keys():
            schema_names[ee['schema_name']]=ee['schema_name']

    for schema_name in schema_names:
        schema={}
        schema['name']=schema_name
        tables=[]
        for ee in inputs_js['extracts']:
            if ee['schema_name'] == schema_name:
                table={}
                table['name']=csv_filename(ee)
                table['columns']=col_defs[csv_filename(ee)]
                table['keys']=ee['unique_key_columns']
                tables.append(table)
        schema['tables']=tables
        schemas_vect.append(schema)
    
    schemas['schemas']=schemas_vect


    return  schemas


def csv_filename(extract):
    return   os.path.join(extract['schema_name'],extract['table_name']+'.csv')


def create_bag(inputs_js): 

    host = inputs_js['mssql_server']['dns']
    database = inputs_js['mssql_server']['database_name']
    user = inputs_js['mssql_server']['user_name']
    password = inputs_js['mssql_server']['db_password']

    bag_dir, ba  = os.path.splitext(inputs_js['bag']['bag_path'])

    bag_archiver = ba.replace('.','').lower()

    if os.path.exists(bag_dir):
        print "Passed bag directory [%s] already exists....deleting it...." % bag_dir
        shutil.rmtree(bag_dir)

    col_defs={}
    for extract in inputs_js['extracts']:
        sql_file=extract['query_file']
        csv_file = csv_filename(extract)

        
        conn = pyodbc.connect(dsn=host, database=database, user=user, password=password,charset='UTF8')    
        cursor = conn.cursor()
        sql = read_query(sql_file)
        cursor.execute(sql)
  
        col_types=[]  
        for colinfo in cursor.description:
            dd={}
            dd['type']=csvescape(py_dic[colinfo[1]])
            dd['name']=csvescape(colinfo[0])
            col_types.append(dd)

        col_defs[csv_file]=col_types
        csv_file_rel=os.path.join(bag_dir,csv_file)
        write_csv(cursor,csv_file_rel) 


    schema_file=write_schema(inputs_js,col_defs)

    with open(os.path.join(bag_dir,'schemas.js'), 'wb') as f:
        json.dump(schema_file, f,indent=3,encoding="utf-8",sort_keys=True)

    manifest=write_manifest(inputs_js,col_defs)
 
    with open(os.path.join(bag_dir,'sql2csv_manifest.js'), 'wb') as f:
        json.dump(manifest, f,indent=3,encoding="utf-8")

    bag = bagit.make_bag(bag_dir,{'Contact-Name': 'Alejandro Bugacov'})

    try:
        bag.validate()        
        sys.stdout.write('[sql2bag] Created valid data bag: %s \n' % bag_dir )
                
    except bagit.BagValidationError as e:
        print "BagValidationError:", e
        for d in e.details:
            if isinstance(d, bag.ChecksumMismatch):
                print "expected %s to have %s checksum of %s but found %s" % (e.path, e.algorithm, e.expected, e.found)
    except:
        print "Unexpected error in Validating Bag:", sys.exc_info()[0]
        raise


    if bag_archiver is not None:
        try:
            archive_bag(bag_dir, bag_archiver.lower())
        except Exception as e:
            print "Unexpected error while creating data bag archive:", e
            raise SystemExit(1)
        finally:
            cleanup_bag(bag_dir)


    return bag

        
def main(argv):
    
    if len(argv) != 2:
        sys.stderr.write(""" 
usage: python sql2bag.py <sql2bag-config.json> 

<sql2bag-config.json>: json input file. See below for configuration example file.

The sql2bag.py utility reads SQL server and queries inputs from the configuration file and the creates a bag in the location passed as  "bag_path" 
value of the configuration file.

sql2bag-config.json
{
    "bag":
    {
      "bag_path":"example_files/test_bag"
    },
    "mssql_server":
    {
      "server_name":"bugacov.isi.edu",
      "dns": "gpcr",
      "database_name":"rce",
      "user_name":"sa",
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


1) "dns" is the Data Source Name used in the ODBC connector. 
2) Each query_file must contain a properly writen query in SQL.

""")
        sys.exit(1)

    bag = create_bag(read_json(argv[1])) 
    sys.exit(0)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
