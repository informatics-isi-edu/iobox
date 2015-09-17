
#
# Coverts the Metadata xlsx file to CSV files and the creates a bag  
# Creates one CSV file for each of the passed Worksheets contained in the 
# Workbook. 
#
# The CSV file is the table encountered after the row_offset (passed also as argument) 
# for each Worksheet. The row_offset can be the row number or the value entered in the 
# cell(row_offset,1)
#



import sys
import datetime
import json
import shutil
import bagit

import os.path
import xlrd
import csv
import sys
from xlrd.sheet import ctype_text 


def get_rowheader(s,row_offset):
    print row_offset
    print type(row_offset)
    rowheader=-1
    if isinstance(row_offset,int): 
        rowheader=row_offset
    elif isinstance(row_offset,basestring):
        for rownum in xrange(s.nrows):
            cell_obj=s.cell(rownum,0)
            if cell_obj.value == row_offset:
                rowheader = rownum+1
                break
    else:
        print "ERROR [xls2bag] Can't handle type of passed row_offset=%s" % type(row_offset)
        sys.exit(1)
    
    if rowheader == -1:
        print "ERROR [xls2bag] Can's compute the offset row to locate header row"
        sys.exit(1)

    return rowheader


def get_col_index(s,irow,val):
    for icol in xrange(s.ncols):
        try: 
            if s.cell(irow,icol).value == val:
                return icol
        except Exception, e:
            sys.stderr.write("ERROR [xls2bag]: Cannot find column index with header [%s] \n" % val)
            sys.stderr.write("Exception: %s\n" % str(e))
            sys.exit(1)

def format_header(val):
    return val.strip().replace(' ','_').lower()

# It assumes that:
#      1) if row_offset is an int, then that's the row number of the header row
#      2) if row_offset is a string, then finds the row with cell in column 0 
#         matching the string and then assumes that the next row is the header
#

def write_table(s,row_offset,col1,num_cols,refs,ref_col,wr):

    rowheader = get_rowheader(s,row_offset)
    col1_index = get_col_index(s,rowheader,col1)

    # this is for the parent table wich has a refereced column.
    # will treat composed keys later
    if ref_col != "NULL":
        ref_index = get_col_index(s,rowheader,ref_col)
        refs.append(ref_col)

    ref_row=0

    for rowid in range(rowheader,s.nrows):
        # Conver header fields to lower and replace blanks by '_'
        #print "======>>> Row=%s" % rowid
        if rowid == rowheader:
            head = [] 
            if ref_col == "NULL":
                head.append(format_header(refs[ref_row]))
            for colid in range(col1_index,(col1_index+num_cols)):
                head.append(format_header(s.cell(rowid,colid).value))
            print head
            wr.writerow(head)
        else:
            row = []
            cell_obj=s.cell(rowid,col1_index)
            cell_type_str = ctype_text.get(cell_obj.ctype, 'unknown type')

            if cell_type_str == 'empty' and ctype_text.get(s.cell(rowid-1,col1_index).ctype, 'unknown type') != 'empty' and ref_col == "NULL":
                ref_row+=1

            if cell_type_str != 'empty':
                if ref_col == "NULL":
                    row.append(refs[ref_row])
                
                for colid in range(col1_index,(col1_index+num_cols)):
                    row.append(s.cell(rowid,colid).value)
                wr.writerow(row)
                if ref_col != "NULL":
                    refs.append(s.cell(rowid,ref_index).value)


    return refs


def wsheet2csv(xls_file,worksheet,row_offset,tables,out_dir):

    print 'out_dir=%s' % out_dir

    try:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
    except OSError:
        sys.stderr.write("Cannot create bag directory\n")
        sys.exit(1)

    try:
        wb = xlrd.open_workbook(xls_file)
    except OSError:
        sys.stderr.write("Cannot open excel file=%s\n" % xls_file)
        sys.stderr.write("Exception %s" % exc_info()[1])
        sys.exit(1)


    if isinstance(worksheet,int): 
        ws= wb.sheet_by_index(worksheet)        
    elif isinstance(row_offset,basestring): 
        ws= wb.sheet_by_name(worksheet)        
    else:
        print "ERROR [wsheet2csv] Can't handle type of passed worksheet=%s" % type(row_offset)
        sys.exit(1)

    print '=== Worksheet name:',ws.name

    refs=[]
    for tt in tables:
        col1= tt['first_column']
        num_cols =  tt['num_columns']
        ref_col = tt['referenced']
        print tt['name']
        print tt['first_column']
        print tt['num_columns']
        print ref_col

        try:
            csvfile = out_dir+'/'+ws.name+'-'+tt['name']+'.csv'
            csvf = open(csvfile, 'wb')
            wr = csv.writer(csvf, quoting=csv.QUOTE_ALL)
        except IOError:
            sys.stderr.write("Cannot open csv file=%s\n" % csvfile )
            sys.exit(1)

        refs = write_table(ws,row_offset,col1,num_cols,refs,ref_col,wr)

def read_json(input_file):
    json_input=open(input_file).read()
    return json.loads(json_input)


def bagdir(bag_dir,bag_archiver):
    bag = bagit.make_bag(bag_dir,{'Contact-Name': 'Alejandro Bugacov'})

    try:
        bag.validate()
        sys.stdout.write('[xls2bag] Created valid data bag: %s \n' % bag_dir )

    except bagit.BagValidationError as e:
        print "BagValidationError:", e
        for d in e.details:
            if isinstance(d, bag.ChecksumMismatch):
                print "expected %s to have %s checksum of %s but found %s" % (e.path, e.algorithm, e.expected, e.found)
    except:
        print "Unexpected error in Validating Bag:", sys.exc_info()[0]
        raise

    
    """if bag_archiver is not None:
        try:
            archive_bag(bag_dir, bag_archiver.lower())
        except Exception as e:
            print "Unexpected error while creating data bag archive:", e
            raise SystemExit(1)
        finally:
            cleanup_bag(bag_dir)"""

    return bag


def create_bag(inputs_js):
    bag_dir, ba  = os.path.splitext(inputs_js['bag']['bag_path'])
    bag_archiver = ba.replace('.','').lower()

    if os.path.exists(bag_dir):
        print "Passed bag directory [%s] already exists....deleting it...." % bag_dir
        shutil.rmtree(bag_dir)

    xls_file = inputs_js['excel']['xls_file']

    print "================================================"
    print "Bag dir=%s" % bag_dir
    print "Archiver=%s" % bag_archiver
    print "Excel File=%s" % xls_file

    for ws in inputs_js['excel']['worksheets']:
        worksheet = ws['worksheet']
        row_offset = ws['offset_row']
        tables = ws['tables']
        print "worksheet=%s" % worksheet
        print "Offset Row=%s" % row_offset
        print "Tables=%s" % tables
        wsheet2csv(xls_file,worksheet,row_offset,ws['tables'],bag_dir)

    print "================================================"
    
    return bagdir(bag_dir,bag_archiver)



def main(argv):
    if len(argv) != 2:
        sys.stderr.write("""
    usage: python xls2bag.py <xls2bag-conf.json> 
    Converts the xls file to bag format based on worksheets and table description passed in the 
    configiation file  <xls2bag-conf.json>. 
    Each worksheet in the xls file can have up to two nested tables of the form 

The structure for the configuration file is:

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
                 {"name":"T1",
                  "first_column":"T11",
                  "num_columns":3,
                  "referenced":"T11"
                 },
                 {"name":"T2",
                  "first_column":"T21",
                  "num_columns":4,
                  "referenced":"NULL"
                 }
             ]
           }
       ]
    }
}
 
        """)
        sys.exit(1)


    bag = create_bag(read_json(argv[1]))
    sys.exit(0)
        

if __name__ == '__main__':
    sys.exit(main(sys.argv))
            
