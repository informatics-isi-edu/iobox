#
# Copyright 2015 University of Southern California
# Distributed under the Apache License, Version 2.0. See LICENSE for more info.
#

""" Installation script for the IObox utilities.
"""

from setuptools import setup, find_packages

setup(
    name="iobox",
    description="ETL utilities for ERMrest+HATRAC",
    url='https://github.com/informatics-isi-edu/iobox/',
    maintainer='USC Information Sciences Institute ISR Division',
    maintainer_email='misd-support@isi.edu',
    version="0.1-prerelease",
    packages=find_packages(),
    package_data={'iobox.sql2bag': ['data/*.*']},
    scripts=['bin/sql2dams.py',
             'bin/dams2bag.py',
             'bin/bag2dams.py',
             'bin/schema2dot.py',
             'bin/xls2bag.py',
             'bin/xml2bag.py'],
    requires=[
        'cookielib',
        'csv',
        'datetime',
        'httplib',
        'json',
        'optparse',
        'os',
        'os.path',
        'simplejson',
        'shutil',
        'sys',
        'zipfile',
        'tarfile',
        'tempfile',
        'urlparse',
        'xml'],
    install_requires=['ordereddict',
                      'requests',
                      'pyodbc',
                      'xlrd',
                      'bagit==1.5.4.dev'],
    dependency_links=[
         "https://github.com/informatics-isi-edu/bagit-python/archive/master.zip#egg=bagit-1.5.4.dev"
    ],
    license='Apache 2.0',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ])

