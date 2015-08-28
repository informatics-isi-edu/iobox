#!/usr/bin/python

import sys
import shutil
import requests
import cookielib
import zipfile
import urlparse
import tarfile
import os.path
import tempfile
import bagit
import simplejson as json
import ordereddict

requests.packages.urllib3.disable_warnings()


def cleanup_bag(bag_path):
    print "Cleaning up bag: %s" % bag_path
    shutil.rmtree(bag_path)


def read_config(input_file):
    json_input = open(input_file).read()
    return json.loads(json_input, object_pairs_hook=ordereddict.OrderedDict)


def open_session(host, user_data):
    cj = cookielib.CookieJar()
    url = ''.join([host, '/ermrest/authn/session'])
    domain = urlparse.urlsplit(url).netloc

    if user_data is None:
        return

    r = requests.post(url, verify=False, data=user_data)
    if r.status_code > 203:
        print 'Open Session Failed with Status Code: %s %s\n' % (r.status_code, r.text)
        sys.exit(1)

    c = cookielib.Cookie(version=0,
                         name='ermrest',
                         value=r.cookies['ermrest'],
                         port=None,
                         port_specified=None,
                         domain=domain,
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

    cj.set_cookie(c)
    return cj


def put_file(url, input_path, headers, cookie_jar):
    if input_path:
        try:
            with open(input_path, 'rb') as data_file:
                r = requests.put(url, data=data_file, headers=headers, verify=False, cookies=cookie_jar)
                if r.status_code != 200:
                    print 'HTTP PUT Failed for url: %s' % url
                    print "Host %s responded:\n" % urlparse.urlsplit(url).netloc
                    print r.text
                    raise RuntimeError('File [%s] transfer failed. ' % input_path)
                else:
                    print 'File [%s] transfer successful.' % input_path
        except requests.exceptions.RequestException as e:
            print 'HTTP Request Exception: %s %s' % (e.errno, e.message)
        finally:
            data_file.close()


def import_from_bag(config):
    bag_tempdir = None
    bag_config = config['bag']
    bag_path = os.path.abspath(bag_config['bag_path'])
    catalog_config = config['catalog']
    host = catalog_config['host']
    path = catalog_config['path']
    username = catalog_config['username']
    password = catalog_config['password']

    if not os.path.exists(bag_path):
        print("Specified bag path not found: %s" % bag_path)
        sys.exit(2)

    try:
        if os.path.isfile(bag_path):
            bag_tempdir = tempfile.mkdtemp(prefix='bag_')
            if zipfile.is_zipfile(bag_path):
                print "Extracting ZIP archived bag file: %s" % bag_path
                bag_file = file(bag_path, 'rb')
                zipped = zipfile.ZipFile(bag_file)
                zipped.extractall(bag_tempdir)
                zipped.close()
            elif tarfile.is_tarfile(bag_path):
                print "Extracting TAR/GZ/BZ2 archived bag file: %s" % bag_path
                tarred = tarfile.open(bag_path)
                tarred.extractall(bag_tempdir)
                tarred.close()
            else:
                print "Archive format not supported for bag file: %s" % bag_path
                print "Supported archive formats are ZIP or TAR/GZ/BZ2"

            bag_path = os.path.abspath(bag_tempdir)

        try:
            print "Opening bag: %s" % bag_path
            bag = bagit.Bag(bag_path)
            bag.validate()
        except bagit.BagValidationError as e:
            print "BagValidationError:", e
            for d in e.details:
                if isinstance(d, bagit.ChecksumMismatch):
                    raise RuntimeError("Bag %s was expected to have %s checksum of %s but found %s" %
                                       (d.path, d.algorithm, d.expected, d.found))
        except Exception as e:
            raise RuntimeError("Unhandled exception while validating bag:", e)

        consistent = True
        for entity in catalog_config['entities']:
            input_path = os.path.normpath(os.path.join('data', entity['input_path']))
            payload_entries = bag.payload_entries()
            if input_path not in payload_entries:
                consistent = False
                print "A specified entity file was not found in the bag payload: %s" % input_path
                continue
        if not consistent:
            raise RuntimeError(
                "One or more specified input files were not found in the bag payload. "
                "The import process will now be aborted.")

        if username and password:
            cookie_jar = open_session(host, {'username': username, 'password': password})
        else:
            cookie_jar = None

        for entity in catalog_config['entities']:
            url = ''.join([host, path, entity['entity_path']])
            input_path = os.path.abspath(os.path.join(bag_path, 'data', entity['input_path']))
            input_format = entity['input_format']
            if input_format == 'csv':
                headers = {'content-type': 'text/csv'}
            elif input_format == 'json':
                headers = {'content-type': 'application/json'}
            else:
                print "Unsupported input type: %s" % input_format
                continue

            put_file(url, input_path, headers, cookie_jar)

    except RuntimeError as re:
        print "Fatal runtime error:", re
        raise SystemExit(1)
    except Exception as e:
        print "Unhandled exception:", e
        raise SystemExit(1)
    finally:
        if bag_tempdir and os.path.exists(bag_tempdir):
            cleanup_bag(bag_tempdir)


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("""
usage: python bag2dams.py <config_file>
where <config_file> is the full path to the JSON file containing the configuration that will be used to upload
entities and assets to the DAMS \n
""")
        sys.exit(1)

    import_from_bag(read_config(argv[1]))
    sys.exit(0)


if __name__ == '__main__':
    main(sys.argv)
