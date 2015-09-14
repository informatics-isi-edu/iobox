#
# Copyright 2015 University of Southern California
# Distributed under the Apache License, Version 2.0. See LICENSE for more info.
#

""" Installation script for the IObox utilities.
"""

from distutils.core import setup

setup(
    name="iobox",
    description="ETL utilities for ERMrest+HATRAC",
    url='https://github.com/informatics-isi-edu/iobox/',
    maintainer='USC Information Sciences Institute ISR Division',
    maintainer_email='misd-support@isi.edu',
    version="0.1-prerelease",
    packages=['iobox', 'iobox.bag2dams', 'iobox.dams2bag', 'iobox.sql2bag'],
    package_data={'iobox.sql2bag': ['data/*.*']},
    scripts=['bin/sql2dams.py', 'bin/dams2bag.py', 'bin/bag2dams.py'],
    requires=[
        'bagit',
        'cookielib',
        'csv',
        'datetime',
        'json',
        'ordereddict',
        'os',
        'os.path',
        'pyodbc',
        'requests',
        'simplejson',
        'shutil',
        'sys',
        'zipfile',
        'tarfile',
        'tempfile',
        'urlparse'],
    license='Apache 2.0',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ])

