import sys
import cookielib
import shutil
import os.path
import urlparse
import requests
import bagit
import simplejson as json

CHUNK_SIZE = 1024 * 1024
requests.packages.urllib3.disable_warnings()


def cleanup_bag(bag_path):
    shutil.rmtree(bag_path)


def read_config(input_file):
    config = open(input_file).read()
    return json.loads(config)


def open_session(host, user_data):
    cj = cookielib.CookieJar()
    url = ''.join([host, '/ermrest/authn/session'])
    domain = urlparse.urlsplit(url).netloc

    if user_data is None:
        return

    r = requests.post(url, verify=False, data=user_data)
    if r.status_code > 203:
        sys.stdout.write('Open Session Failed with Status Code: %s %s\n' % (r.status_code, r.text))
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


def get_file(query_url, output_path, output_format, cookie_jar):
    if output_path:
        try:
            if not output_format:
                output_format = 'csv'
            if output_format == 'csv':
                headers = {'content-type': 'text/csv', 'accept': 'text/csv'}
                output_path = ''.join([output_path, '.csv'])
            elif output_format == 'json':
                headers = {'content-type': 'application/json', 'accept': 'application/json'}
                output_path = ''.join([output_path, '.json'])

            r = requests.get(query_url, headers=headers, stream=True, verify=False, cookies=cookie_jar)
            if r.status_code != 200:
                sys.stdout.write('Query Failed for url: %s\n' % query_url)
                sys.stdout.write('Transfer Failed for file [%s]. Status code: %s %s \n\n' %
                                 (output_path, r.status_code, r.text))
                sys.exit(1)
            else:
                sys.stdout.write('File [%s] transfer successful. Status code: %s \n' % (output_path, r.status_code))
                data_file = open(output_path, 'wb')
                for chunk in r.iter_content(CHUNK_SIZE):
                    data_file.write(chunk)
                data_file.flush()
                data_file.close()
        except requests.exceptions.RequestException as e:
            sys.stdout.write('HTTP Request Exception: %s %s \n' % (e.errno, e.message))


def create_bag(config):
    bag_path = config['BAG_PATH']
    contact = config['CONTACT_NAME']
    host = config['HOST']
    base_path = config['BASE_PATH']
    username = config['USER_NAME']
    password = config['PASSWORD']

    print "Creating bag: %s" % bag_path

    if os.path.exists(bag_path):
        print "Specified bag directory [%s] already exists....deleting it...." % bag_path
        shutil.rmtree(bag_path)

    os.makedirs(bag_path)

    if username and password:
        cookie_jar = open_session(host, {'username': username, 'password': password})
    else:
        cookie_jar = None

    for query in config['QUERIES']:
        query_url = ''.join([host, base_path, query['query_path']])
        output_file = query['output_file']
        output_format = query['output_format']
        output_path = os.path.abspath(''.join([bag_path, os.path.sep, output_file]))
        get_file(query_url, output_path, output_format, cookie_jar)

    bag = bagit.make_bag(bag_path, {'Contact-Name': contact})

    try:
        bag.validate()
        sys.stdout.write('Created valid data bag: %s \n' % bag_path)

    except bagit.BagValidationError as e:
        print "BagValidationError:", e
        for d in e.details:
            if isinstance(d, bag.ChecksumMismatch):
                print "expected %s to have %s checksum of %s but found %s" % (d.path, d.algorithm, d.expected, d.found)
    except:
        print "Unexpected error in Validating Bag:", sys.exc_info()[0]
        raise

    try:
        archive = shutil.make_archive(bag_path, 'zip', bag_path)
        sys.stdout.write('Created valid data bag archive: %s \n' % archive)
    except:
        print 'Unexpected error while creating data bag archive: ', sys.exc_info()[0]
        raise

    return bag


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("""
usage: python dams2bag.py <config_file>
where <config_file> is the full path to the JSON file containing the configuration that will be used to download assets
from the DAMS \n
""")
        sys.exit(1)

    create_bag(read_config(argv[1]))
    sys.exit(0)


if __name__ == '__main__':
    main(sys.argv)
