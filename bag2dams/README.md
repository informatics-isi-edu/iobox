The `bag2dams` utility consumes a BagIt package, authenticates
to an ERMrest store, and makes one or more entity POST or PUT requests to load
the data from the BagIt package. It also loads the assets to a Hatrac store (TBD).

### Prerequisites
1. Python 2.6 or higher
2. Python requests
3. Python bagit

### Installation
1. Install additional Python libraries:
    * pip install pyodbc
    * pip install bagit
    * pip install requests
2. From the source distribution base directory, run:
    * python setup.py install

### Execution
1. From the bag2dams/bag2dams directory, run:
    * ./bag2dams /path/to/config/file

### Structure of the bag2dams configuration file:
The input to bag2dams.py is a JSON file. This JSON file contains a single object which has the following structure:

```json
{
  "bag":
  {
    "bag_path":"/path/to/bag.zip"
  },
  "catalog":
  {
    "host": "https://your-host.org",
    "path": "/ermrest/catalog/1",
    "username": "",
    "password": "",
    "entities":
    [
      {
        "entity_path": "/entity/myschema:myentity",
        "input_path": "samples/mysampledata.csv",
        "input_format": "csv"
      }
    ],
    "assets":
    [
      {
        "asset_url": "https:some-host/path",
        "input_path": "samples/some/file/asset",
        "mime-type": "image/x.nifti"
      }
    ]
  }
}
```

### Configuration parameter definitions
1. `bag` object:
    *   `bag_path`: The full path to the input bag. This path may represent an archive file (zip,tar,tgz,bz2) or a directory.

        Example: ```"bag_path":"/path/to/bag.zip"```
        
2. `catalog` object:
    *   `host`: The base URL to the target ERMRest instance.
    
        Example: ```"https://your-host.org"```

    *   `path`: The path to the destination catalog of the target ERMRest instance.
    
        Example: ```"path": "/ermrest/catalog/1"```

    *   `username`: The user name to use when authenticating to the target ERMRest instance.

        Example: ```"username": "someuser"```
        
    *   `password`: The password to use when authenticating to the target ERMRest instance.

        Example: ```"password": "*****"```
        
    *   `entities`: An array of parameters, one per target entity, that specify input source, format and target entity.
        *   `entity_path`: The target entity path on the target ERMRest instance where the data will be posted.
        
            Example: ```"entity_path": "/entity/myschema:myentity"```
        *   `input_path`: The relative path to the source file from the bag's "data" payload directory.
            
            Example: ```"input_path": "samples/mysampledata.csv"```
        *   `input_format`: The data format of the input file -- currently "csv" and "json" are supported.
            
            Example: ```"input_format": "csv"```

    * `assets`: An array of parameters, one per target file, that specify source, mime-type, and target path.  NOTE: asset upload functionality is currently unimplemented and parameters are subject to change.
        * `asset_url`: The target URL on the destination system.
        * `input_path`: The relative path to the source file from the bag's "data" payload directory. 
        * `mime-type`: The mime-type that reflects the asset data.


