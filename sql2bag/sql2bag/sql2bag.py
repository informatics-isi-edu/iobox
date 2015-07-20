#!/usr/bin/python

import os
import pyodbc
import csv
import sys
import datetime
import json

import bagit


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
        return v.isoformat(' ')
    elif type(v) in [int, float, str]:
        return '%s' % str(v)
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

    with open(csv_file,'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)

    for row in cursor:
        values = []
        for i in range(0, len(row)):
            values.append(val2text(row[i]).encode("utf-8"))
        with open(csv_file,'a') as f:
            writer = csv.writer(f)
            writer.writerow(values)


def write_manifest(inputs_js,col_defs):

    manifest={}
    extracts =[]
    for ee in inputs_js['EXTRACTS']:
        extract={}
        extract['table_data']=csv_filename(ee)
        extract['schema_name']=ee['schema_name']
        extract['table_name']=ee['table_name']
        extract['column_definitions']=col_defs[csv_filename(ee)]
        extract['object_columns']=ee['bulk_data_columns']        
        extracts.append(extract)

    manifest['extracts']=extracts
    manifest['source']=inputs_js['SERVER_NAME']
    manifest['destination']=inputs_js['DESTINATION_SERVER_NAME']
    manifest['destination_user_name']=inputs_js['DESTINATION_USER_NAME']
    manifest['destination_password']=inputs_js['DESTINATION_PASSWORD']

    return manifest


def write_schema(inputs_js,col_defs):


    schemas={}
    schemas_vect=[]
    
    schema_names={}
    for ee in inputs_js['EXTRACTS']:
        if ee['schema_name'] not in schema_names.keys():
            schema_names[ee['schema_name']]=ee['schema_name']

    for schema_name in schema_names:
        schema={}
        schema['name']=schema_name
        tables=[]
        for ee in inputs_js['EXTRACTS']:
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
    #return  extract['schema_name']+PATH_SEP+extract['table_name']+'.csv'
    return   os.path.join(extract['schema_name'],extract['table_name']+'.csv')


def create_bag(inputs_js,bag_dir): 
    host = inputs_js['DNS']
    database = inputs_js['DATABASE_NAME']
    user = inputs_js['USER_NAME']
    password = inputs_js['DB_PASSWORD']

    col_defs={}
    for extract in inputs_js['EXTRACTS']:
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
        #csv_file_rel=bag_dir+PATH_SEP+csv_file
        csv_file_rel=os.path.join(bag_dir,csv_file)
        write_csv(cursor,csv_file_rel)

    schema_file=write_schema(inputs_js,col_defs)

    #with open(bag_dir+PATH_SEP+'schemas.js', 'w') as f:
    with open(os.path.join(bag_dir,'schemas.js'), 'w') as f:
        json.dump(schema_file, f,indent=3,encoding="utf-8",sort_keys=True)

    manifest=write_manifest(inputs_js,col_defs)
 
    with open(os.path.join(bag_dir,'sql2csv_manifest.js'), 'w') as f:
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


    return bag

        
def main(argv):
    
    if len(argv) != 3:
        sys.stderr.write(""" 
usage: python sql2bag.py <input_file.js> <bag_name>

<input_file.js>: reads input from <input_file.js> file. See below for format example. 
<bag_name>: creates a bag under bagit specifications under the location passed as <bag_name>
 
input_file.js example:
{
    "SERVER_NAME":"mssqlserver.isi.edu",
    "DNS": "gpcr",
    "DATABASE_NAME":"DB_NAME",
    "USER_NAME":"db_username",
    "EXTRACTS": [
         { "query_file" : "sql_construct.sql",
           "schema_name": "gpcr",
           "table_name" : "construct",
           "bulk_data_columns" : [],
           "unique_key_columns": ["id"]
         },
         { "query_file" : "sql_cont_target.sql",
           "schema_name": "gpcr",
           "table_name" : "cont_target",
           "bulk_data_columns" : [],
           "unique_key_columns": ["id"]
         }
    ]
}

1) DNS is the Data Source Name used in the ODBC connector. 
2) Each query_file must contain a properly writen query in SQL.

""")
        sys.exit(1)

    inputs_js=read_json(argv[1])
    bag_path=argv[2]
    bag = create_bag(inputs_js,bag_path) 


if __name__ == '__main__':
    sys.exit(main(sys.argv))
