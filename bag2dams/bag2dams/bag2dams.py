
#curl -b COOKIE -c COOKIE -k -d username=bugacov -d password='*******'  https://vm-dev-029.misd.isi.edu/ermrest/authn/session
#curl -k -b COOKIE -c COOKIE  -w "%{http_code}\n"  -T "Target.csv" -H "Content-Type: text/csv"  -X PUT  
#                                       https://vm-dev-029.misd.isi.edu/ermrest/catalog/1/entity/bag_test:target

import re
import sys 
import requests
import csv 
import cookielib

import os.path
import bagit
import json


PATH_SEP=os.path.sep
SQL2BAG_MANIFEST='sql2csv_manifest.js'

def read_json(input_file):
    json_input=open(input_file).read()
    return json.loads(json_input)


# loads the csv files in the bag
def load_bag_csv(bag_path):
    bag = bagit.Bag(bag_path)

    try:
        bag.validate()        
        sys.stdout.write('----- Bag [%s] is valid----\n' % bag_path)    

        #for path, fixity in bag.entries.items():
        #    print "path:%s md5:%s" % (path, fixity["md5"])
        
        inputs = read_json(bag_path+PATH_SEP+'data'+PATH_SEP+SQL2BAG_MANIFEST)

        #url = 'https://vm-dev-029.misd.isi.edu/ermrest/catalog/1/entity/bag_test:target'
        base_url='https://'+inputs['destination']+'/ermrest/catalog/1/entity'

        print "Base URL=%s" % base_url 

        udata={'username':inputs['destination_user_name'],'password':inputs['destination_password']}

        cjar = open_session(udata)

        for path,fixity in bag.entries.items():
            if os.path.splitext(path)[1].lower() == '.csv':
                if  re.search('Target',path):
                    put_csv_file(inputs,bag_path+'/'+path,base_url,cjar)

    except bagit.BagValidationError as e:
        print "BagValidationError:", e
        for d in e.details:
            if isinstance(d, bag.ChecksumMismatch):
                print "expected %s to have %s checksum of %s but found %s" % (e.path, e.algorithm, e.expected, e.found)
    except:
        print "Unexpected error in Validating Bag:", sys.exc_info()[0]
        raise

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

    print r.status_code
    cj.set_cookie(c)
    return cj


# not doing any table schema validation at this point....
# assumes file has .csv extension
# file_fn is the full name of the file relative to the bag. I.e.: bag_path/data/schema_name/file_name.csv
def put_csv_file(inputs,file_fn,base_url,cookiejar):

    sys.stdout.write('Full File Name=%s \n' % os.path.abspath(file_fn))

    fn = re.findall('data/[^/]+/[^/]+.csv$',file_fn,flags=re.IGNORECASE)
 
    if len(fn)>0:   
        fn2 = re.split('/',os.path.splitext(fn[0])[0])
        schema_name = fn2[1].lower()
        file_name = fn2[2].lower()
        sys.stdout.write('Schema Name=%s  Table Name=%s \n' % (schema_name,file_name))

        print cookiejar
        fname = os.path.abspath(file_fn)
   
        print fname
        print schema_name
        print file_name

        with open (fname,'rb') as data_file:
            url = base_url+'/'+schema_name+':'+file_name
            print url
            headers = {'content-type': 'text/csv'}
            r = requests.put(url, data=data_file, headers=headers,verify=False,cookies=cookiejar)
            print r.status_code


def main(argv):

    if len(argv) != 2:
        sys.stderr.write("usage: python bag2dams.py <bag_name>")
        sys.exit(1)

    print "LOADING BAG=%s" % argv[1]
    load_bag_csv(argv[1])


if __name__ == '__main__':
    sys.exit(main(sys.argv))

