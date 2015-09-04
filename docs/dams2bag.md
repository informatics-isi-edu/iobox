The `dams2bag` utility authenticates to an ERMRest store, makes one or more entity or attribute GET requests, and produces a BagIt package.


### Prerequisites
1. Python 2.6 or higher
2. Python requests
3. Python bagit

### Installation
1. Install additional Python libraries:
    * pip install bagit
    * pip install requests

2. From the source distribution base directory, run:
    * python setup.py install

### Execution
1. From the dams2bag/dams2bag directory, run:
    * ./dams2bag /path/to/config/file

### Structure of the dams2bag configuration file:
The input to dams2bag.py is a JSON file. This JSON file contains a single object which has the following structure:
```json
{
  "bag":
  {
    "bag_path": "/path/to/bag",
    "bag_archiver":"zip",
    "bag_metadata":
    {
      "Source-Organization": "USC Information Sciences Institute, Informatics Systems Research Division",
      "Contact-Name": "Mike D'Arcy",
      "External-Description": "A bag containing summary data and links to images (via fetch.txt) matching a set of filter criteria",
      "Internal-Sender-Identifier": "USC-ISI-IRSD"
    }
  },
  "catalog":
  {
    "host": "https://your-host.org",
    "path": "/ermrest/catalog/1",
    "username": "someuser",
    "password": "********",
    "queries":
    [
      {
        "query_path": "/entity/A:=myschema:mytable/mycolumn1=Yes/mycolumn2=No/mycolumn3=42/$A@sort(mycolumn1)",
        "schema_path": "/schema/myschema/table/mytable",
        "output_name": "myschema/mytable",
        "output_format": "csv"
      },
      {
        "query_path": "/attribute/A:=myschema:mytable/mycolumn1=Yes/mycolumn2=No/mycolumn3=42/$A/F:=FILES/URL:=F:uri,LENGTH:=F:bytes,FILENAME:=F:filepath",
        "output_name": "myschema/images",
        "output_format": "fetch"
      }
    ]
  }
}
```
### Configuration parameter definitions
1. `bag` object:
    *   `bag_path`: The full path to the input bag. This path must represent a directory.

        Example: ```"bag_path":"/path/to/bag"```

    *   `bag_archiver`: The archive format used to serialize the newly created bag. This parameter is optional.  If specified, valid values are:
        * `zip`
        * `tar`
        * `tgz`
        * `bz2`

        Example: ```"bag_archiver":"tgz"```

        Note that if this optional attribute is omitted from the JSON structure, the bag will still be created but not serialized.

    *   `bag_metadata`: This parameter is a list of JSON attribute-value pairs that will be written verbatim as metadata to the bag's bag-info.txt.

2. `catalog` object:
    *   `host`: The base URL to the target ERMRest instance.

        Example: ```"https://your-host.org"```

    *   `path`: The path to the destination catalog of the target ERMRest instance.

        Example: ```"path": "/ermrest/catalog/1"```

    *   `username`: The user name to use when authenticating to the target ERMRest instance.

        Example: ```"username": "someuser"```

    *   `password`: The password to use when authenticating to the target ERMRest instance.

        Example: ```"password": "*****"```

    *   `queries`: An array of parameters, one per target entity, that specify the query path, the output path relative to the bag data directory, the output format, and optional schema output.

        *   `query_path`: The query path on the target ERMRest instance from which the data will be downloaded.

            Example: ```"/attribute/A:=myschema:mytable/mycolumn1=Yes/mycolumn2=No/mycolumn3=42/$A/F:=FILES/URL:=F:uri,LENGTH:=F:bytes,FILENAME:=F:filepath"```

        *   `output_name`: The relative path to the destination file from the bag's "data" payload directory.

            Example: ```"output_name": "myschema/images"```

        *   `output_format`: The data format of the output file, currently `csv`, `json`, `fetch`, and `prefetch` are supported.  Note that `fetch` and `prefetch` are special cases, both of which require data to be returned as tuples of file attributes of the form ```(URL, LENGTH, FILENAME)```.  In the `fetch` mode, these tuples are written directly to the BagIt optional file `fetch.txt` and in the `prefetch` mode, the tool will parse each tuple and attempt to automatically retrieve the file referenced by `URL` and place it in the directory referenced by `FILENAME`, relative to the bag's payload directory.

            Example: ```"output_format": "prefetch"```


