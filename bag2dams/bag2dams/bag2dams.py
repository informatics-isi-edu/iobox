
#curl -b COOKIE -c COOKIE -k -d username=bugacov -d password='*******'  https://vm-dev-029.misd.isi.edu/ermrest/authn/session
#curl -k -b COOKIE -c COOKIE  -w "%{http_code}\n"  -T "Target.csv" -H "Content-Type: text/csv"  -X PUT  
#                                       https://vm-dev-029.misd.isi.edu/ermrest/catalog/1/entity/bag_test:target

import re
import sys 
import requests
import csv 
import cookielib
import shutil 
import collections

import os.path
import bagit
import json

import simplejson as json
import ordereddict



#from requests.packages.urllib3.exceptions import InsecureRequestWarning 
#requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

requests.packages.urllib3.disable_warnings()

PATH_SEP=os.path.sep
SQL2BAG_MANIFEST='sql2csv_manifest.js'


def cleanup_bag(bag_path):
    shutil.rmtree(bag_path)


def read_json(input_file):
    json_input=open(input_file).read()
    return json.loads(json_input)

def ordered_read_json(input_file):
    json_input=open(input_file).read()
    return json.loads(json_input,object_pairs_hook=ordereddict.OrderedDict)


# loads the csv files in the bag

def load_bag_csv(inputs_js,bag_path):
    bag = bagit.Bag(bag_path)

    try:
        bag.validate()        
        
        #for path, fixity in bag.entries.items():
        #    print "path:%s md5:%s" % (path, fixity["md5"])
        
        #inputs = read_json(bag_path+PATH_SEP+'data'+PATH_SEP+SQL2BAG_MANIFEST)
        inputs = read_json(os.path.join(bag_path,'data',SQL2BAG_MANIFEST))


        # convert EXTRACT part to ordered dict 

        oextracts = ordered_read_json(inputs_js)

        #url = 'https://vm-dev-029.misd.isi.edu/ermrest/catalog/1/entity/bag_test:target'
        base_url='https://'+inputs['destination']+'/ermrest/catalog/1/entity'

        udata={'username':inputs['destination_user_name'],'password':inputs['destination_password']}

        cjar = open_session(udata)

        # do this hack to load tables in the same order as they are given in the input json file
        for ee in oextracts['EXTRACTS']:
            for path,fixity in bag.entries.items():
                if os.path.splitext(os.path.basename(path))[0].lower() == ee['table_name'].lower(): 
                #if os.path.splitext(path)[1].lower() == '.csv':
                    put_csv_file(inputs,bag_path+PATH_SEP+path,base_url,cjar)


    except bagit.BagValidationError as e:
        sys.stdout.write('=== Bag [%s] is not valid \n' % bag_path)
        print "BagValidationError:", e
        for d in e.details:
            if isinstance(d, bag.ChecksumMismatch):
                print "expected %s to have %s checksum of %s but found %s" % (e.path, e.algorithm, e.expected, e.found)
        sys.exit(2)
    except:
        print "Unexpected error in Validating Bag:", sys.exc_info()[0]
        raise
        sys.exit(2)

def open_session(user_data):
    cj=cookielib.CookieJar()
    url = 'https://vm-dev-029.misd.isi.edu/ermrest/authn/session'
    r = requests.post(url,verify=False,data=user_data)
    c =cookielib.Cookie(version=0, 
                        name='ermrest', 
                        value=r.cookies['ermrest'], 
                        port=None, 
                        port_specified=None, 
                        domain='vm-dev-029.misd.isi.edu', 
                        domain_specified=False, 
                        domain_initial_dot=False, 
                        path='/', 
                        path_specified=True, 
                        secure=True, 
                        expires=None, 
                        discard=True, 
                        comment=None, 
                        comment_url=None, 
                        rest={'HttpOnly': None}, 
                        rfc2109=False)
    
    if r.status_code > 203:
        sys.stdout.write('=== Open Session Failed with Status Code=%s\n' % r.status_code)
        sys.exit(1)

    cj.set_cookie(c)
    return cj


# not doing any table schema validation at this point....
# assumes file has .csv extension
# file_fn is the full name of the file relative to the bag. I.e.: bag_path/data/schema_name/file_name.csv
def put_csv_file(inputs,file_fn,base_url,cookiejar):

    #sys.stdout.write('=== Full File Name=%s \n' % os.path.abspath(file_fn))

    fn = re.findall('data/[^/]+/[^/]+.csv$',file_fn.replace('\\','/'),flags=re.IGNORECASE)
 
    if len(fn)>0:   
        fn2 = re.split('/',os.path.splitext(fn[0])[0])
        schema_name = fn2[1].lower()
        file_name = fn2[2].lower()
        #sys.stdout.write('Schema Name=%s  Table Name=%s \n' % (schema_name,file_name))

        #print cookiejar
        fname = os.path.abspath(file_fn)
   
        with open (fname,'rb') as data_file:
            url = base_url+'/'+schema_name+':'+file_name
            headers = {'content-type': 'text/csv'}
            r = requests.put(url, data=data_file, headers=headers,verify=False,cookies=cookiejar)
            if r.status_code != 200: 
                sys.stdout.write('===      Failed url: %s\n' % url)
                sys.stdout.write('===      Failed Status code for table %s= %s \n\n' % (file_name,r.status_code))
            else:
                sys.stdout.write('=== Table [%s] transfer OK. Status code= %s \n' % (file_name,r.status_code))


def main(argv):

    if len(argv) != 3:
        sys.stderr.write("""
usage: python bag2dams.py <inputs_file> <bag_name> 
where <bag_name> is the path directory of the '"'bag'"' containing the data that will be uploaded to the DAMS \n
""")
        sys.exit(1)

    print "LOADING BAG=%s" % argv[1]
    load_bag_csv(argv[1],argv[2])

if __name__ == '__main__':
    sys.exit(main(sys.argv))

