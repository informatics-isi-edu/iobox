#!/usr/bin/python

import sys
import logging
import time
import cookielib
import shutil
import os.path
import urlparse
import requests
import csv
import bagit
import zipfile
import tarfile
import simplejson as json
import ordereddict

CHUNK_SIZE = 1024 * 1024
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
        raise RuntimeError('Open Session Failed with Status Code: %s %s\n' % (r.status_code, r.text))
    else:
        logger.info("Session established: %s", url)
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
                logger.error('HTTP GET Failed for url: %s' % url)
                logger.error("Host %s responded:\n\n%s" % (urlparse.urlsplit(url).netloc,  r.text))
                raise RuntimeError('File [%s] transfer failed. ' % output_path)
            else:
                with open(output_path, 'wb') as data_file:
                    for chunk in r.iter_content(CHUNK_SIZE):
                        data_file.write(chunk)
                    data_file.flush()
                logger.info('File [%s] transfer successful.' % output_path)
        except requests.exceptions.RequestException as e:
            raise RuntimeError('HTTP Request Exception: %s %s' % (e.errno, e.message))


def archive_bag(bag_path, bag_archiver):
    logger.info("Archiving bag (%s): %s" % (bag_archiver, bag_path))

    tarmode = None
    archive = None
    fn = '.'.join([os.path.basename(bag_path), bag_archiver])
    if bag_archiver == 'tar':
        tarmode = 'w'
    elif bag_archiver == 'tgz':
        tarmode = 'w:gz'
    elif bag_archiver == 'bz2':
        tarmode = 'w:bz2'
    elif bag_archiver == 'zip':
        zfp = os.path.join(os.path.dirname(bag_path), fn)
        zf = zipfile.ZipFile(zfp, 'w', allowZip64=True)
        for dirpath, dirnames, filenames in os.walk(bag_path):
            for name in filenames:
                filepath = os.path.normpath(os.path.join(dirpath, name))
                relpath = os.path.relpath(filepath, os.path.dirname(bag_path))
                if os.path.isfile(filepath):
                    zf.write(filepath, relpath)
        zf.close()
        archive = zf.filename
    else:
        raise RuntimeError("Archive format not supported for bag file: %s \n "
                           "Supported archive formats are ZIP or TAR/GZ/BZ2" % bag_path)

    if tarmode:
        tfp = os.path.join(os.path.dirname(bag_path), fn)
        t = tarfile.open(tfp, tarmode)
        t.add(bag_path, os.path.relpath(bag_path, os.path.dirname(bag_path)), recursive=True)
        t.close()
        archive = t.name

    logger.info('Created bag archive: %s' % archive)


def export_to_bag(config_file, quiet=False):

    if quiet:
        requests.packages.urllib3.disable_warnings()
    configure_logging(logging.WARN if quiet else logging.INFO)
    logger.info("Reading config file: %s" % config_file)

    try:
        config = read_config(config_file)
        bag_config = config['bag']
        bag_path = os.path.abspath(bag_config['bag_path'])
        bag_archiver = bag_config.get('bag_archiver', None)
        bag_metadata = bag_config.get('bag_metadata', {})
        bag_update = bag_config.get('bag_update', False)
        catalog_config = config['catalog']
        host = catalog_config['host']
        path = catalog_config['path']
        username = catalog_config['username']
        password = catalog_config['password']
    except Exception as e:
        raise RuntimeError('Error parsing configuration: %s' % e)

    if 'Bag-Software-Agent' not in bag_metadata:
        bag_metadata['Bag-Software-Agent'] = 'bagit.py <http://github.com/ini-bdds/bagit-python>'

    if os.path.exists(bag_path) and not bag_update:
        saved_bag_path = ''.join([bag_path, '_', time.strftime("%Y-%m-%d_%H.%M.%S")])
        logger.warn("Specified bag directory already exists -- moving it to %s" % saved_bag_path)
        logger.info("An existing bag may be updated by setting the parameter "
                    "\"bag_update\" to True in the \"bag\" section of the configuration file. ")
        shutil.move(bag_path, saved_bag_path)

    if not os.path.exists(bag_path):
        os.makedirs(bag_path)
        bag = bagit.make_bag(bag_path, bag_metadata, 1, ['sha256'])
    else:
        bag = bagit.Bag(bag_path)

    if username and password:
        cookie_jar = open_session(host, {'username': username, 'password': password})
    else:
        cookie_jar = None

    for query in catalog_config['queries']:
        url = ''.join([host, path, query['query_path']])
        output_name = query.get('output_name', None)
        output_path = query['output_path']
        output_format = query['output_format']
        schema_path = query.get('schema_path', None)
        schema_output_path = os.path.abspath(os.path.join(bag_path, 'data', ''.join([output_path, '-schema.json'])))

        try:
            if output_format == 'csv':
                headers = {'accept': 'text/csv'}
                output_path = ''.join([os.path.join(output_path, output_name) if output_name else output_path, '.csv'])
                output_dir = os.path.abspath(os.path.join(bag_path, 'data', output_path))
            elif output_format == 'json':
                headers = {'accept': 'application/json'}
                output_path = ''.join([os.path.join(output_path, output_name) if output_name else output_path, '.json'])
                output_dir = os.path.abspath(os.path.join(bag_path, 'data', output_path))
            elif output_format == 'prefetch':
                headers = {'accept': 'text/csv'}
                output_dir = os.path.abspath(
                    ''.join([os.path.join(bag_path, output_name) if output_name else 'prefetch-manifest', '.txt']))
            elif output_format == 'fetch':
                headers = {'accept': 'text/csv'}
                output_dir = os.path.abspath(
                    ''.join([os.path.join(bag_path, output_name) if output_name else 'fetch-manifest', '.txt']))
            else:
                raise RuntimeError("Unsupported output type: %s" % output_format)

            get_file(url, output_dir, headers, cookie_jar)

            if schema_path:
                schema_url = ''.join([host, path, schema_path])
                get_file(schema_url, schema_output_path, {'accept': 'application/json'}, cookie_jar)

            if output_format == 'prefetch':
                logger.info("Prefetching file(s)...")
                with open(output_dir, 'rb') as csv_in:
                    reader = csv.DictReader(csv_in)
                    try:
                        for row in reader:
                            prefetch_url = row['url']
                            prefetch_length = int(row['length'])
                            prefetch_filename = \
                                os.path.abspath(os.path.join(bag_path, 'data', output_path, row['filename']))
                            logger.info("Prefetching %s as %s" % (prefetch_url, prefetch_filename))
                            get_file(prefetch_url, prefetch_filename, headers, cookie_jar)
                            file_bytes = os.path.getsize(prefetch_filename)
                            if prefetch_length != file_bytes:
                                raise RuntimeError("File size of %s does not match expected size of %s for file %s" %
                                                   (prefetch_length, file_bytes, prefetch_filename))
                    finally:
                        csv_in.close()
                        os.remove(output_dir)

            elif output_format == 'fetch':
                logger.info("Adding remote file references from %s" % output_dir)
                csv_in = open(output_dir, 'rb')
                reader = csv.DictReader(csv_in)
                for row in reader:
                    row['filename'] = ''.join(['data', '/', output_path, '/', row['filename']])
                    checksums = ['md5', 'sha1', 'sha256', 'sha512']
                    for checksum in checksums:
                        # url, length, filename, alg, digest
                        if checksum in row:
                            bag.add_remote_file(
                                row['url'], row['length'], row['filename'], checksum, row[checksum])
                csv_in.close()
                os.remove(output_dir)

        except RuntimeError as e:
            logger.fatal("Fatal runtime error: %s", e)
            if not bag_update:
                cleanup_bag(bag_path)
            raise e

    try:
        logger.info("Updating bag manifests...")
        bag.save(1, manifests=True)
    except Exception as e:
        logger.fatal("Exception while updating bag manifests: %s", e)
        if not bag_update:
            cleanup_bag(bag_path)
        raise e

    logger.info('Created bag: %s' % bag_path)

    try:
        logger.info("Validating bag...")
        bag.validate(1, fast=False)
        logger.info('Bag validated successfully: %s' % bag_path)
    except bagit.BagIncompleteError as e:
        logger.warn("BagIncompleteError: %s %s", e,
                    "This validation error may be transient if the bag contains unresolved remote file references "
                    "from a fetch.txt file. In this case the bag is incomplete but not necessarily invalid. ")
    except bagit.BagValidationError as e:
        logger.warn("BagValidationError: %s", e)
        for d in e.details:
            if isinstance(d, bagit.ChecksumMismatch):
                logger.warn("Bag %s was expected to have %s checksum of %s but found %s" %
                            (d.path, d.algorithm, d.expected, d.found))

    if bag_archiver is not None:
        try:
            archive_bag(bag_path, bag_archiver.lower())
            cleanup_bag(bag_path)
        except Exception as e:
            logger.error("Unexpected error while creating data bag archive:", e)
            raise e

    return bag

