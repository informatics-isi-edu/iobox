#!/usr/bin/python

import sys
import logging
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

logger = logging.getLogger(__name__)


def configure_logging(level=logging.INFO, logpath=None):
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    if logpath:
        logging.basicConfig(filename=logpath, level=level, format=log_format)
    else:
        logging.basicConfig(level=level, format=log_format)


def cleanup_bag(bag_path):
    logger.info("Cleaning up bag dir: %s" % bag_path)
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

    if user_data['password'] and user_data['username']:
        r = requests.post(url, verify=False, data=user_data)
        cvalue = r.cookies['ermrest']
        if r.status_code > 203:
            raise RuntimeError('Open Session Failed with Status Code: %s %s\n' % (r.status_code, r.text))
        else:
            logger.info("Session established: %s", url)
    elif user_data['cookie_value']:
        cvalue = user_data['cookie_value']
    else:
        raise RuntimeError('No valid authentication method found to open a connection.')

    logger.debug("Cookie Value: %s" % cvalue)

    c = cookielib.Cookie(version=0,
                         name='ermrest',
                         value=cvalue,
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
                    logger.error('HTTP PUT Failed for url: %s' % url)
                    logger.error("Host %s responded:\n\n%s" % (urlparse.urlsplit(url).netloc,  r.text))
                    raise RuntimeError('File [%s] transfer failed. ' % input_path)
                else:
                    logger.info('File [%s] transfer successful.' % input_path)
        except requests.exceptions.RequestException as e:
            raise RuntimeError('HTTP Request Exception: %s %s' % (e.errno, e.message))


def get_url(url, cookie_jar):

    logger.info("URL: %s \n" % url)
    try:
        r = requests.get(url, verify=False, cookies=cookie_jar)
    except requests.exceptions.RequestException as e:
        raise RuntimeError('HTTP Request Exception: %s %s' % (e.errno, e.message))

    logger.info(r.text)


def test_catalog_connection(config):
    catalog_config = config['catalog']
    host = catalog_config['host']
    path = catalog_config['path']
    username = catalog_config['username']
    password = catalog_config['password']
    cookie_value = catalog_config['cookie_value']

    if username and password:
        cookie_jar = open_session(host, {'username': username, 'password': password, 'cookie_value': ""})
    elif cookie_value:
        logger.info("Found Cookie Value: %s" % cookie_value)
        cookie_jar = open_session(host, {'username': "", 'password': "", 'cookie_value': cookie_value})
    else:
        cookie_jar = None

    url = ''.join([host, path, '/meta'])
    get_url(url, cookie_jar)


def test_entities(cfg):
    config = read_config(cfg)
    catalog_config = config['catalog']
    bag_config = config['bag']
    bag_path = os.path.abspath(bag_config['bag_path'])
    host = catalog_config['host']
    path = catalog_config['path']

    for entity in catalog_config['entities']:
        url = ''.join([host, path, entity['entity_path']])
        input_path = os.path.abspath(os.path.join(bag_path, 'data', entity['input_path']))
        input_format = entity['input_format']

        logger.info("URL: %s\n" % url)


def import_from_bag(config_file, quiet=False):

    if quiet:
        requests.packages.urllib3.disable_warnings()
    configure_logging(logging.WARN if quiet else logging.INFO)
    logger.info("Reading config file: %s" % config_file)

    try:
        config = read_config(config_file)
        bag_tempdir = None
        bag_config = config['bag']
        bag_path = os.path.abspath(bag_config['bag_path'])
        catalog_config = config['catalog']
        host = catalog_config['host']
        path = catalog_config['path']
        username = catalog_config['username']
        password = catalog_config['password']
        cookie_value = catalog_config.get('cookie_value', None)
    except Exception as e:
        raise RuntimeError('Error parsing configuration: %s' % e)

    if not os.path.exists(bag_path):
        raise RuntimeError("Specified bag path not found: %s" % bag_path)

    try:
        if os.path.isfile(bag_path):
            bag_tempdir = tempfile.mkdtemp(prefix='bag_')
            if zipfile.is_zipfile(bag_path):
                logger.info("Extracting ZIP archived bag file: %s" % bag_path)
                bag_file = file(bag_path, 'rb')
                zipped = zipfile.ZipFile(bag_file)
                zipped.extractall(bag_tempdir)
                zipped.close()
            elif tarfile.is_tarfile(bag_path):
                logger.info("Extracting TAR/GZ/BZ2 archived bag file: %s" % bag_path)
                tarred = tarfile.open(bag_path)
                tarred.extractall(bag_tempdir)
                tarred.close()
            else:
                raise RuntimeError("Archive format not supported for bag file: %s"
                                   "\nSupported archive formats are ZIP or TAR/GZ/BZ2" % bag_path)

            for dirpath, dirnames, filenames in os.walk(bag_tempdir):
                if len(dirnames) > 1:
                    # According to the spec there should only ever be one base bag directory at the base of a
                    # deserialized archive. It is not clear if other non-bag directories are allowed.
                    # For now, assume no other dirs allowed and terminate if more than one present.
                    raise RuntimeError(
                        "Invalid bag serialization: Multiple base directories found in extracted archive.")
                else:
                    bag_path = os.path.abspath(os.path.join(dirpath, dirnames[0]))
                    break

        logger.info("Opening bag: %s" % bag_path)
        bag = bagit.Bag(bag_path)

        try:
            logger.info("Validating bag: %s" % bag_path)
            bag.validate()
        except bagit.BagIncompleteError as e:
            logger.warn("BagIncompleteError: %s %s", e,
                        "This validation error may be transient if the bag contains unresolved remote file references "
                        "from a fetch.txt file. In this case the bag is incomplete but not necessarily invalid. "
                        "Resolve remote file references (if any) and re-validate.")
            raise e
        except bagit.BagValidationError as e:
            logger.error("BagValidationError:", e)
            for d in e.details:
                if isinstance(d, bagit.ChecksumMismatch):
                    raise RuntimeError("Bag %s was expected to have %s checksum of %s but found %s" %
                                       (d.path, d.algorithm, d.expected, d.found))
        except Exception as e:
            raise RuntimeError("Unhandled exception while validating bag: %s" % e)

        consistent = True
        for entity in catalog_config['entities']:
            input_path = os.path.normpath(os.path.join('data', entity['input_path']))
            payload_entries = bag.payload_entries()
            if input_path not in payload_entries:
                consistent = False
                logger.warn("A specified entity file was not found in the bag payload: %s" % input_path)
                continue
        if not consistent:
            raise RuntimeError(
                "One or more specified input files were not found in the bag payload. "
                "The import process will now be aborted.")

        if username and password:
            cookie_jar = open_session(host, {'username': username, 'password': password, 'cookie_value': ""})
        elif cookie_value:
            # logger.info("Found Cookie Value: %s" % cookie_value)
            cookie_jar = open_session(host, {'username': "", 'password': "", 'cookie_value': cookie_value})
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
                logger.error("Unsupported input type: %s" % input_format)
                continue

            put_file(url, input_path, headers, cookie_jar)

    except RuntimeError as re:
        logger.error("Fatal runtime error: %s", re)
        raise re
    except Exception as e:
        logger.error("Unhandled exception: %s", e)
        raise e
    finally:
        if bag_tempdir and os.path.exists(bag_tempdir):
            cleanup_bag(bag_tempdir)
