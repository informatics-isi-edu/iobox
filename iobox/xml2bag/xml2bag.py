#!/usr/bin/python
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


"""
This script generates the CSV files from the XML files.
Each CSV file corresponds to a SQL table name.
The CSV files are packed in a beanbag.

Parameters:

    - config: the configuration file

The configuration file contains a JSON object with the following keys:

    - "host": the host for the ermrest
    - "catalog": the catalog number (the database)
    - "schema": the schema name
    - "xml": the directory containing the XML files,
    - "thumbnail": the directory with the thumbnails files,
    - "thumbnail_url": the URL path for the thumbnails files,
    - "csv": the output directory where the CSV files and the beanbag will be generated

Usage:
    python xml2bag.py <config_file>
    
"""

import sys
import os
import shutil
from optparse import OptionParser
import json
import xml.etree.ElementTree as ET
from httplib import HTTPSConnection, OK
import bagit
import zipfile

parser = OptionParser()
parser.header = {}
parser.add_option('-c', '--config', action='store', dest='config', type='string', help='Configuration file')

(options, args) = parser.parse_args()

if not options.config:
    print 'ERROR: Missing configuration file'
    sys.exit(1)
    
tablesNames = []
tablesDefinitions = {}
tablesReferences = {}
tablesSortedNames = []
tablesData = {}
columnTypes = {}
schemaDefinition = None

"""
Get the file name w/o its extension
"""
def get_file_name(filename):
    return '.'.join(filename.split('.')[0:-1])

"""
Class for the configuration parameters
"""
class ConfigClient (object):

    def __init__(self, **kwargs):
        self.options = kwargs.get("options")
        self.cfg = None
        
    """
    Read the JSON configuration file
    """
    def load(self):
        self.cfg = {}
        if os.path.exists(self.options.config):
            f = open(self.options.config, 'r')
            try:
                self.cfg = json.load(f)
            except ValueError as e:
                sys.stderr.write('Malformed configuration file: %s\n' % e)
                sys.exit(1)
            else:
                f.close()
        else:
            sys.stderr.write('Configuration file: "%s" does not exist.\n' % self.options.config)
            sys.exit(1)
            
    """
    Validate the configuration parameters
    """
    def validate(self):
        self.host = self.cfg.get('host', None)
        if not self.host:
            sys.stderr.write('Ermrest host name must be given.\n')
            sys.exit(1)
        self.catalog = self.cfg.get('catalog', None)
        if not self.catalog:
            sys.stderr.write('Ermrest catalog must be given.\n')
            sys.exit(1)
        self.schema = self.cfg.get('schema', None)
        if not self.schema:
            sys.stderr.write('Ermrest schema must be given.\n')
            sys.exit(1)
        self.input = self.cfg.get('xml', None)
        if not self.input:
            sys.stderr.write('Input directory must be given.\n')
            sys.exit(1)
        if not os.path.exists(self.input):
            sys.stderr.write('Input directory must exist.\n')
            sys.exit(1)
        self.thumbnails = {}
        self.thumbnail = self.cfg.get('thumbnail', None)
        if self.thumbnail and os.path.exists(self.thumbnail):
            for f in os.listdir(self.thumbnail):
                self.thumbnails[get_file_name(f)] = f
        self.thumbnail_url = self.cfg.get('thumbnail_url', None)
        self.output = self.cfg.get('csv', None)
        if not self.output:
            sys.stderr.write('Output directory must be given.\n')
            sys.exit(1)
        if os.path.exists(self.output):
            shutil.rmtree(self.output)
        os.makedirs('%s/bag' % self.output)
        self.file = '%s/csv.txt' % self.output
        self.zip = '%s/bag.zip' % self.output
        self.dams = '%s/bag.conf' % self.output
        self.output = '%s/bag' % self.output
        
            
    """
    Get a configuration parameter
    """
    def get(self, field):
        if field=='host':
            return self.host
        elif field=='catalog':
            return self.catalog
        elif field=='schema':
            return self.schema
        elif field=='input':
            return self.input
        elif field=='output':
            return self.output
        elif field=='file':
            return self.file
        elif field=='zip':
            return self.zip
        elif field=='dams':
            return self.dams
        elif field=='thumbnails':
            return self.thumbnails
        elif field=='thumbnail_url':
            return self.thumbnail_url
        else:
            return None
        
"""
Class for ermrest communication
"""
class ErmrestClient (object):

    def __init__(self, **kwargs):
        self.host = kwargs.get("host")
        self.schema = kwargs.get("schema")
        self.catalog = kwargs.get("catalog")
        self.webconn = None
        self.headers = dict(Accept='application/json')
        
    """
    Open an ermrest connection
    """
    def connect(self):
        self.webconn = HTTPSConnection(self.host)
            
    """
    Send an ermrest GET request
    """
    def get_request(self, url):
        self.webconn.request('GET', url, '', self.headers)
        resp = self.webconn.getresponse()
        if resp.status != OK:
            sys.stderr.write('Unexpected HTTP status: %d' % resp.status)
            sys.exit(1)
        return resp
    
    """
    GET the schema introspection
    """
    def get_schema(self):
        resp = self.get_request('/ermrest/catalog/%d/schema/%s' % (self.catalog, self.schema))
        res = json.loads(resp.read())
        return res
    
    """
    Initialize the tables indexes
    """
    def load(self, db_schema, tables):
        tables_names = []
        for key,value in db_schema['tables'].iteritems():
            tables_names.append(key)
        for db_table in tables_names:
            resp = self.get_request('/ermrest/catalog/%d/aggregate/%s:%s/max:=max(id)' % (self.catalog, self.schema, db_table))
            res = json.loads(resp.read())
            max_val = res[0]['max']
            if max_val==None:
                max_val = 0
            tables[db_table] = {}
            tables[db_table]['id'] = max_val
            tables[db_table]['data'] = []
            
"""
Class for XML parsing
"""
class XMLClient (object):
    
    def __init__(self, **kwargs):
        self.input = kwargs.get("input")
        self.tablesNames = kwargs.get("tablesNames")
        self.tablesDefinitions = kwargs.get("tablesDefinitions")
        self.tablesReferences = kwargs.get("tablesReferences")
        self.tablesData = kwargs.get("tablesData")
        self.columnTypes = kwargs.get("columnTypes")
        self.schemaDefinition = kwargs.get("schemaDefinition")
        self.files=[f for f in os.listdir(self.input) if f.endswith('.xml')]
        self.thumbnails = kwargs.get("thumbnails")
        self.thumbnail_url = kwargs.get("thumbnail_url")

        
    """
    Process the input directory with the XML files
    """
    def process_input(self):
        for f in self.files:  
            self.process_XML_file(f) 
        
    """
    Parse an XML file
    """
    def process_XML_file(self, f):
        tree = ET.parse('%s/%s' % (self.input, f))
        root = tree.getroot()
        self.process_file(f, root, None)
        
    """
    Populate the data structures for the SQL tables
    """
    def process_file(self, f, elem, parent):
        
        """
        Check for the thumbnail table
        """
        if self.hasThumbnailColumn(elem.tag):
            if elem.tag not in self.tablesNames:
                self.tablesNames.append(elem.tag)
            if elem.tag not in self.tablesDefinitions.keys():
                self.tablesDefinitions[elem.tag] = []
            if 'thumbnail' not in self.tablesDefinitions[elem.tag]:
                self.tablesDefinitions[elem.tag].append('thumbnail')
                self.setType(elem.tag, 'thumbnail', 'text')
        
        hasAttributes = len(elem.attrib.keys()) > 0
        
        """
        Process the XML attributes
        """
        if hasAttributes:
            if elem.tag not in self.tablesNames:
                self.tablesNames.append(elem.tag)
            if elem.tag not in self.tablesDefinitions.keys():
                self.tablesDefinitions[elem.tag] = []
            if parent!=None and elem.tag not in self.tablesReferences.keys():
                self.tablesReferences[elem.tag] = []
            if parent!=None and parent.tag not in self.tablesReferences[elem.tag]:
                self.tablesReferences[elem.tag].append(parent.tag)
            for attr,value in elem.attrib.items():
                attrib = attr
                if attrib not in self.tablesDefinitions[elem.tag]:
                    self.tablesDefinitions[elem.tag].append(attrib)
                    self.setType(elem.tag, attrib, self.getType(elem.tag, attrib, value))
    
        """
        Process the XML element
        """
        if len(elem)==0:
            if parent==None:
                sys.stderr.write('Unexpected parent: None')
                sys.exit(1)
            if not hasAttributes:
                if elem.tag not in self.tablesDefinitions[parent.tag]:
                    self.tablesDefinitions[parent.tag].append(elem.tag)
            else:
                if elem.tag not in self.tablesDefinitions[elem.tag]:
                    self.tablesDefinitions[elem.tag].append(elem.tag)
            if self.isMultiValue(elem, parent):
                self.setType(parent.tag, elem.tag, 'text')
            else:
                self.setType(parent.tag, elem.tag, self.getType(parent.tag, elem.tag, elem.text))
        else:
            if not hasAttributes:
                if elem.tag not in self.tablesNames:
                    self.tablesNames.append(elem.tag)
                if elem.tag not in self.tablesDefinitions.keys():
                    self.tablesDefinitions[elem.tag] = []
                if parent!=None and elem.tag not in self.tablesReferences.keys():
                    self.tablesReferences[elem.tag] = []
                if parent!=None and parent.tag not in self.tablesReferences[elem.tag]:
                    self.tablesReferences[elem.tag].append(parent.tag)
            for child in elem:
                self.process_file(f, child, elem)
        
    """
    Get the column type from the schema
    """
    def getColumnType(self, table, column):
        if table in self.schemaDefinition['tables']:
            column_definitions = self.schemaDefinition['tables'][table]['column_definitions']
            for col_def in column_definitions:
                if col_def['name'] == column:
                    return col_def['type']['typename']
        return None
        
    """
    Check if a table has a thumbnail column
    """
    def hasThumbnailColumn(self, table):
        if table in self.schemaDefinition['tables']:
            column_definitions = self.schemaDefinition['tables'][table]['column_definitions']
            for col_def in column_definitions:
                if col_def['name'] == 'thumbnail':
                    return True
        return False
        
    """
    Guess the type of a value
    """
    def getType(self, table, column, value):
        ret = self.getColumnType(table, column)
        if ret != None:
            return ret
        try:
            v = int(value)
            return 'int4'
        except:
            try:
                v = float(value)
                return 'float8'
            except:
                return 'text'
        
    """
    Check if the tag is an array
    """
    def isMultiValue(self, elem, parent):
        count = 0
        for child in parent:
            if child.tag==elem.tag:
                count += 1
        return count >= 2
        
    """
    Set the SQL type of a value
    """
    def setType(self, table, column, col_type):
        if table not in self.columnTypes.keys():
            self.columnTypes[table] = {}
        if column not in self.columnTypes[table].keys():
            self.columnTypes[table][column] = col_type
        
    """
    Load the data from the XML files
    """
    def load_data(self):
        for f in self.files:  
            tree = ET.parse('%s/%s' % (self.input, f))
            root = tree.getroot()
            self.load_file_data(f, root, None, None) 
        
    """
    Load the data from an XML file
    """
    def load_file_data(self, f, elem, parent, parent_obj):
        obj = {}
        
        """
        Load the thumbnail value
        """
        if self.hasThumbnailColumn(elem.tag) and get_file_name(f) in self.thumbnails:
            obj['thumbnail'] = '%s/%s' % (self.thumbnail_url, self.thumbnails[get_file_name(f)])

        hasAttributes = len(elem.attrib.keys()) > 0
        
        """
        Load the attributes
        """
        if hasAttributes or len(elem)>0:
            if elem.tag not in self.tablesData.keys():
                self.tablesData[elem.tag] = {}
                self.tablesData[elem.tag]['id'] = 0
                self.tablesData[elem.tag]['data'] = []
            self.tablesData[elem.tag]['id'] = self.tablesData[elem.tag]['id']+1
            self.tablesData[elem.tag]['data'].append(obj)
            obj['id'] = self.tablesData[elem.tag]['id']
            if parent!=None and elem.tag in self.tablesReferences.keys() and parent.tag in self.tablesReferences[elem.tag]:
                col = '%s_id' % parent.tag
                obj[col] = self.tablesData[parent.tag]['id']
        if hasAttributes:
            for attr,value in elem.attrib.items():
                attrib = attr
                obj[attrib] = value
                
        """
        Load the element
        """
        if len(elem)==0:
            value = elem.text
            if value!=None:
                if self.isMultiValue(elem, parent):
                    value = self.getMultiValue(elem, parent)
                if hasAttributes:
                    obj[elem.tag] = value
                else:
                    parent_obj[elem.tag] = value
        else:
            for child in elem:
                self.load_file_data(f, child, elem, obj)
        
    """
    Get the multi value of a tag
    """
    def getMultiValue(self, elem, parent):
        value = []
        for child in parent:
            if child.tag==elem.tag:
                value.append(child.text)
        return ','.join(value)
        
"""
Class for generating CSV files
"""
class CSVClient (object):
    
    def __init__(self, **kwargs):
        self.csvFiles = None
        self.file = kwargs.get("file")
        self.output = kwargs.get("output")
        self.tablesNames = kwargs.get("tablesNames")
        self.tablesSortedNames = kwargs.get("tablesSortedNames")
        self.tablesReferences = kwargs.get("tablesReferences")
        self.tablesData = kwargs.get("tablesData")
        self.tablesDefinitions = kwargs.get("tablesDefinitions")
        self.columnTypes = kwargs.get("columnTypes")
        
        
    """
    Sort the tables to be created based on the dependencies (references)
    """
    def sortTablesDefinitions(self):
        sorted = False
        while not sorted:
            sorted = True
            for t in self.tablesNames:
                if t not in self.tablesSortedNames:
                    if t not in self.tablesReferences.keys():
                        self.tablesSortedNames.append(t)
                        sorted = False
                    else:
                        resolved = True
                        for refTable in self.tablesReferences[t]:
                            if refTable not in self.tablesSortedNames:
                                resolved = False
                                break
                        if resolved:
                            self.tablesSortedNames.append(t)
                            sorted = False
        
    """
    Load the CSV files
    """
    def load_data(self):
        self.csvFiles = open('%s' % self.file, 'w')
        for table in self.tablesSortedNames:
            self.insert_csv_data(table)
        self.csvFiles.close()
        
    """
    Set a CSV value
    """
    def csvValue(self, value):
        if isinstance(value,basestring):
            value = value.replace('"','""')
            value = '"%s"' % value.encode('utf8')
        else:
            value = str(value)
        return value
        
    """
    Insert the data for a table
    """
    def insert_csv_data(self, table):
        if table in self.tablesData.keys():
            self.csvFiles.write('%s/%s.csv\n' % (self.output, table))
            out = open('%s/%s.csv' % (self.output, table), 'w')
            colsDefs = ['id']
            colsDefs.extend(self.tablesDefinitions[table])
            if table in self.tablesReferences.keys():
                colsRef = []
                for col in self.tablesReferences[table]:
                    colsRef.append('%s_id' % col)
                colsDefs.extend(colsRef)
            out.write('%s\n' % ','.join(colsDefs))
            for data in self.tablesData[table]['data']:
                row = []
                for col in colsDefs:
                    if col in data.keys():
                        row.append(self.csvValue(data[col]))
                    else:
                        row.append('')
                out.write('%s\n' % ','.join(row))
            out.close()

"""
Class for generating a bean bag
"""
class BagClient (object):
    
    def __init__(self, **kwargs):
        self.zip = kwargs.get("zip")
        self.output = kwargs.get("output")
        self.contact = kwargs.get("contact")
        self.dams = kwargs.get("dams")
        self.host = kwargs.get("host")
        self.catalog = kwargs.get("catalog")
        self.schema = kwargs.get("schema")
        self.tablesSortedNames = kwargs.get("tablesSortedNames")
        
    """
    Make a beanbag for the CSV files
    """
    def makeBag(self):
        bagit.make_bag(self.output,{'Contact-Name': self.contact})
        
    """
    Zip the beanbag
    """
    def zipBag(self):
        zf = zipfile.ZipFile(self.zip, mode='w')
        crt_path = os.getcwd()
        os.chdir(self.output)
        for root, dirs, files in os.walk('.'):
            for filename in files:
                zf.write('%s/%s' % (root, filename))
        zf.close()
        os.chdir(crt_path)
        
    """
    Generate the configuration file for loading the beanbag into the database
    """
    def damsConfig(self):
        config = {}
        bag = {'bag_path': self.zip}
        config['bag'] = bag
        catalog = {}
        catalog['host'] = 'https://%s' % self.host
        catalog['path'] = '/ermrest/catalog/%d' % self.catalog
        entities = []
        for table in self.tablesSortedNames:
            entity = {}
            entity['entity_path'] = '/entity/%s:%s' % (self.schema, table)
            entity['input_path'] = 'data/%s.csv' % (table)
            entity['input_format'] = 'csv'
            entities.append(entity)
        catalog['entities'] = entities
        config['catalog'] = catalog
        out = open('%s' % (self.dams), 'w')
        out.write('%s\n' % json.dumps(config, indent=4))
        out.close()
        
        
"""
Get the configuration
"""
config_client = ConfigClient(options=options)
config_client.load()
config_client.validate()

"""
Get the ermrest data
"""
ermrest_client = ErmrestClient(host=config_client.get('host'), catalog=config_client.get('catalog'), schema=config_client.get('schema'))
ermrest_client.connect()
schemaDefinition = ermrest_client.get_schema()
ermrest_client.load(schemaDefinition, tablesData)

"""
Parse the XML files
"""
xml_client = XMLClient(input=config_client.get('input'), thumbnails=config_client.get('thumbnails'), thumbnail_url=config_client.get('thumbnail_url'), tablesNames=tablesNames, tablesDefinitions=tablesDefinitions, tablesReferences=tablesReferences, columnTypes=columnTypes, tablesData=tablesData, schemaDefinition=schemaDefinition)
xml_client.process_input()
xml_client.load_data()

"""
Generate the CSV files
"""
csv_client = CSVClient(tablesNames=tablesNames, tablesSortedNames=tablesSortedNames, tablesReferences=tablesReferences, columnTypes=columnTypes, tablesData=tablesData, file=config_client.get('file'), output=config_client.get('output'), tablesDefinitions=tablesDefinitions)
csv_client.sortTablesDefinitions()
csv_client.load_data()

"""
Generate the beanbag
"""
bag_client = BagClient(zip=config_client.get('zip'), output=config_client.get('output'), contact='Serban Voinea', dams=config_client.get('dams'), host=config_client.get('host'), catalog=config_client.get('catalog'), schema=config_client.get('schema'), tablesSortedNames=tablesSortedNames)
bag_client.makeBag()
bag_client.zipBag()
bag_client.damsConfig()

""" DEBUG Traces

print 'tablesNames'
print json.dumps(tablesNames, indent=4) 
print '\n\ntablesDefinitions'
print json.dumps(tablesDefinitions, indent=4) 
print '\n\ntablesReferences'
print json.dumps(tablesReferences, indent=4) 
print '\n\ntablesSortedNames'
print json.dumps(tablesSortedNames, indent=4) 
print '\n\ntablesData'
print json.dumps(tablesData, indent=4) 
print 'columnTypes'
print json.dumps(columnTypes, indent=4) 

"""
sys.exit(0)
