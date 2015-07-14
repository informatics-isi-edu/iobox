
#
# Copyright 2015 University of Southern California
# Distributed under the Apache License, Version 2.0. See LICENSE for more info.
#

from distutils.core import setup

setup(
    name="sql2bag",
    description="converts from SQL to CSV by querying a database through an ODBC connection",
    url='https://github.com/informatics-isi-edu/iobox/tree/master/sql2bag',
    author='misd',
    version="0.1-prerelease",
    packages=['sql2bag'],
    package_dir={'sql2bag': 'sql2bag'},
    include_package_data = True,
    package_data={'sql2bag': ['data/*.*'],},
    requires=['pyodbc', 'csv', 'os', 'sys', 'datetime', 'json', 'bagit'],
    maintainer_email='support@misd.isi.edu',
    license='Apache 2.0',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ])

