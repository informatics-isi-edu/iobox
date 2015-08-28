#!/usr/bin/python

import sys
import cookielib
import shutil
import os.path
import urlparse
import requests
import csv
import bagit
import ordereddict
import simplejson as json

CHUNK_SIZE = 1024 * 1024
requests.packages.urllib3.disable_warnings()


def cleanup_bag(bag_path):
    print "Cleaning up bag: %s" % bag_path
    shutil.rmtree(bag_path)


def read_config(input_file):
    config = open(input_file).read()
    return json.loads(config, object_pairs_hook=ordereddict.OrderedDict)


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


def get_file(url, output_path, headers, cookie_jar):
    if output_path:
        try:
            output_dir = os.path.dirname(os.path.abspath(output_path))
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            r = requests.get(url, headers=headers, stream=True, verify=False, cookies=cookie_jar)
            if r.status_code != 200:
                print 'HTTP GET Failed for url: %s' % url
                print "Host %s responded:\n" % urlparse.urlsplit(url).netloc
                print r.text
                raise RuntimeError('File [%s] transfer failed. ' % output_path)
            else:
                data_file = open(output_path, 'wb')
                for chunk in r.iter_content(CHUNK_SIZE):
                    data_file.write(chunk)
                data_file.flush()
                data_file.close()
                print 'File [%s] transfer successful.' % output_path
        except requests.exceptions.RequestException as e:
            print 'HTTP Request Exception: %s %s' % (e.errno, e.message)


def export_to_bag(config):
    bag_config = config['bag']
    bag_path = os.path.abspath(bag_config['bag_path'])
    bag_archiver = bag_config.get('bag_archiver', None)
    bag_metadata = bag_config.get('bag_metadata', None)
    catalog_config = config['catalog']
    host = catalog_config['host']
    path = catalog_config['path']
    username = catalog_config['username']
    password = catalog_config['password']

    print "Creating bag: %s" % bag_path

    if os.path.exists(bag_path):
        print "Specified bag directory already exists -- it will be deleted"
        shutil.rmtree(bag_path)

    os.makedirs(bag_path)
    bag = bagit.make_bag(bag_path, bag_metadata)

    if username and password:
        cookie_jar = open_session(host, {'username': username, 'password': password})
    else:
        cookie_jar = None

    for query in catalog_config['queries']:
        url = ''.join([host, path, query['query_path']])
        output_name = query['output_name']
        output_format = query['output_format']
        schema_path = query.get('schema_path', None)
        schema_output_path = os.path.abspath(os.path.join(bag_path, 'data', ''.join([output_name, '-schema.json'])))

        if output_format == 'csv':
            headers = {'accept': 'text/csv'}
            output_name = ''.join([output_name, '.csv'])
            output_path = os.path.abspath(os.path.join(bag_path, 'data', output_name))
        elif output_format == 'json':
            headers = {'accept': 'application/json'}
            output_name = ''.join([output_name, '.json'])
            output_path = os.path.abspath(os.path.join(bag_path, 'data', output_name))
        elif output_format == 'prefetch':
            headers = {'accept': 'text/csv'}
            output_path = os.path.abspath(os.path.join(bag_path, 'prefetch.txt'))
        elif output_format == 'fetch':
            headers = {'accept': 'text/csv'}
            output_path = os.path.abspath(os.path.join(bag_path, 'fetch.txt'))
        else:
            print "Unsupported output type: %s" % output_format

        try:
            get_file(url, output_path, headers, cookie_jar)

            if schema_path:
                schema_url = ''.join([host, path, schema_path])
                get_file(schema_url, schema_output_path, {'accept': 'application/json'}, cookie_jar)

            if output_format == 'prefetch':
                print "Prefetching file(s)..."
                with open(output_path, 'rb') as csv_in:
                    reader = csv.DictReader(csv_in)
                    for row in reader:
                        prefetch_url = row['URL']
                        prefetch_length = int(row['LENGTH'])
                        prefetch_filename = \
                            os.path.abspath(os.path.join(bag_path, 'data', output_name, row['FILENAME']))
                        print "Prefetching %s as %s" % (prefetch_url, prefetch_filename)
                        get_file(prefetch_url, prefetch_filename, headers, cookie_jar)
                        file_bytes = os.path.getsize(prefetch_filename)
                        if prefetch_length != file_bytes:
                            print "File size of %s does not match expected size of %s for file %s" % \
                                  (prefetch_length, file_bytes, prefetch_filename)
                            sys.exit(1)
                    csv_in.close()
                    os.remove(output_path)

            elif output_format == 'fetch':
                print "Writing fetch.txt..."
                new_csv_file = ''.join([output_path, '.tmp'])
                with open(output_path, 'rb') as csv_in, open(new_csv_file, 'wb') as csv_out:
                    reader = csv.DictReader(csv_in)
                    writer = csv.DictWriter(csv_out, reader.fieldnames, delimiter='\t')
                    writer.writeheader()
                    for row in reader:
                        row['FILENAME'] = ''.join(['data', '/', output_name, '/', row['FILENAME']])
                        writer.writerow(row)
                    csv_in.close()
                    csv_out.close()
                    os.remove(output_path)
                    os.rename(new_csv_file, output_path)

        except RuntimeError as e:
            print "Fatal runtime error:", e
            cleanup_bag(bag_path)
            raise SystemExit(1)

    try:
        print "Updating bag manifests..."
        bag.save(manifests=True)
        print "Validating bag..."
        bag.validate()
        print 'Created valid data bag: %s' % bag_path

    except bagit.BagValidationError as e:
        print "BagValidationError:", e
        for d in e.details:
            if isinstance(d, bagit.ChecksumMismatch):
                print "Bag %s was expected to have %s checksum of %s but found %s" % \
                      (d.path, d.algorithm, d.expected, d.found)
                cleanup_bag(bag_path)
                raise SystemExit(1)
    except Exception as e:
        print "Unhandled exception while validating bag:", e
        cleanup_bag(bag_path)
        raise SystemExit(1)

    try:
        if bag_archiver is not None:
            archive = shutil.make_archive(bag_path, bag_archiver, bag_path)
            print 'Created data bag archive: %s' % archive
    except Exception as e:
        print "Unexpected error while creating data bag archive:", e
        raise SystemExit(1)
    finally:
        cleanup_bag(bag_path)

    return bag


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("""
usage: python dams2bag.py <config_file>
where <config_file> is the full path to the JSON file containing the configuration that will be used to download assets
from the DAMS \n
""")
        sys.exit(1)

    export_to_bag(read_config(argv[1]))
    sys.exit(0)


if __name__ == '__main__':
    main(sys.argv)
