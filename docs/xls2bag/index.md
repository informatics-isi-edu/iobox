The `xls2bag` utility converts an Excel file (.xls or .xlsx) file into a `bag` conforming the 
BagIt package specifictions. 

The Excel file can have several worksheets and each worksheet can have at most two nested tables with the following structure:


| XLS2BAG_TEST |   |   |   |   |   |   | 
|--------------|---|---|---|---|---|---|
| A1 | A2 | A3  | B1 | B2 | B3 | B4 |
| a11 | a12 | a13 | b11 | b12 | b13 | b14 |
|     |     |     | b21 | b22 | b23 | b24 |
|     |     |     | b31 | b32 | b33 | b34 |
|     |     |     | b41 | b42 | b43 | b44 |
| a21 | a22 | a23 | b51 | b52 | b53 | b54 |
|     |     |     | b61 | b62 | b63 | b64 |
|     |     |     | b71 | b72 | b73 | b74 |

In this example the worksheet has two tables. Table A and Table B. 
Table B can reference a column of Table B. 

The arguments to define the tables are passed in the xls2bag configulation file. 
See below for structure of the configuration file. 

### Prerequisites
1. Python 2.6 or higher
2. Python requests
3. Python bagit

### Installation
1. Install additional Python libraries:
    * pip install bagit
    * pip install requests

    Note: it may be necessary to upgrade the version of the required libraries if they are already installed.  To do this, execute: `pip install --upgrade <library>`

2. From the source distribution base directory, run:
    * python setup.py install

### Execution
1. From the xls2bag directory, run:
    * python xls2bag.py <path_to_configuration_file>

### Structure of the xls2bag configuration file:
The input to xls2bag.py is a JSON file. This JSON file contains a single object which has the following structure:

```json
{                                                                                                                               
    "bag":                                                                                                                      
    {                                                                                                                           
      "bag_path":"data/test_bag"                                                                                                
    },                                                                                                                          
    "excel":                                                                                                                    
    {                                                                                                                           
       "xls_file": "data/xls2bag_test.xlsx",                                                                                    
       "worksheets": [                                                                                                          
           { "worksheet":"TEST1",                                                                                               
             "offset_row":"XLS2BAG_TEST",                                                                                       
             "tables": [                                                                                                        
                 {"name":"A",                                                                                                  
                  "first_column":"A1",                                                                                         
                  "num_columns":3,                                                                                              
                  "referenced":"A1"                                                                                            
                 },                                                                                                             
                 {"name":"B",                                                                                                  
                  "first_column":"B1",                                                                                         
                  "num_columns":4,                                                                                              
                  "referenced":"NULL"                                                                                           
                 }                                                                                                              
             ]                                                                                                                  
           }                                                                                                                    
       ]                                                                                                                        
    }                                                                                                                           
}                                                                                                                               
```

### Configuration parameter definitions
1. `bag` object:
    *   `bag_path`: The full path to the input bag. This path may represent an archive file (zip,tar,tgz,bz2) or a directory.

        Example: ```"bag_path":"/path/to/bag.zip"```
        
2. `excel` object:
    *   `xls_file`: The path to the xls file to converto to bag.
    
        Example: ```"data/xls2bag_test.xlsx"```

   *   `worksheets`: An array of worksheets constained in the Excel file. 
    
   *   `worksheet`: The name or index of the worksheet  

        Example: ```"worksheet": "TEST 1"``` or ```"worksheet": 0``` 
        

   *  `offset_row`: Value in cell(N,1) meaning that the elements of the table start after row N. 
                    If the value entered in this parameter is in cell(N,1), it means that the 
                    header row for the tables in this worksheet starts in row N+1.
       Example: ```"offset_row":"XLS2BAG_TEST"``` 

   *   `tables`:  An array of tables constained in the worksheet. Should not have more than 2 elements. 

   *   `name`: Name of the table
       Exmple" ```"A"```
       
   *   `first_column`: Value of cell of the header for the first column of the table
   *   `num_columns`: Number of columns in the table
   *   `referenced`: Value of cell of the header for the column referenced by the child table. 
                     This value should only not "NULL" in the definition of the parent table and 
                     must be equal to "NULL" in the child table.  

       Example:  
       Parent table:
                 {"name":"A",                                                                                                  
                  "first_column":"A1",                                                                                         
                  "num_columns":3,                                                                                              
                  "referenced":"A1"
                  }
    
       Child table:
                 {"name":"B",                                                                                                  
                  "first_column":"B1",                                                                                         
                  "num_columns":4,                                                                                              
                  "referenced":"NULL"
                  }


With these parameters, xls2bag will create 2 CSV files under the data directory of the bag. 

*   File 1: "TEST 1-A.csv" with table A

A1,A2,A3 
a11,a12,a13 
a21,a22,a23 


*   File 2: "TEST 1-B.csv" with table B

A1,B1,B2,B3,B4 
a11,b11,b12,b13,b14 
a11,b21,b22,b23,b24 
a11,b31,b32,b33,b34 
a11,b41,b42,b43,b44 
a21,b51,b52,b53,b54 
a21,b61,b62,b63,b64 
a21,b71,b72,b73,b74 
  
