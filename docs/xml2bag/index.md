The `xml2bag` utility creates a BagIt package with the CSV files generated from 
the XML files.

The output of the utility consists of the bag.zip and bag.conf files generated on the 
directory specified by the "csv" parameter of the xml2bag configuration file. 
Those two files will be part of the bag2dams configuration file. The bag2dams utility 
loads the bag into the database.

### Prerequisites
1. Python 2.6 or higher
2. Python bagit

### Installation
1. Install additional Python libraries:
    * pip install bagit

2. From the source distribution base directory, run:
    * python setup.py install

### Execution
1. From the xml2bag/xml2bag directory, run:
    * ./xml2bag.py --config /path/to/config/file

### Structure of the xml2bag configuration file:
The input to xml2bag.py is a JSON file. This JSON file contains a single object which has the following structure:

```json
{
  "host": "the_host_for_the_ermrest",
  "catalog": the_catalog_number,
  "schema": "the_schema_name",
  "xml": "the_directory_containing_the_XML_files",
  "thumbnail": "the_directory_containing_the_thumbnails_files",
  "thumbnail_url": "the_URL_path_for_the_thumbnails_files",
  "csv": "the_output_directory_where_the_CSV_files_and_the_beanbag_will_be_generated"
}
```

### Example of configuration file
```json
{
    "host": "multicelldb.misd.isi.edu",
    "catalog": 1,
    "schema": "multicelldb",
    "xml": "input",
    "thumbnail": "thumbnails",
    "thumbnail_url": "/multicelldb_thumbnails",
    "csv": "csv"
}
```
