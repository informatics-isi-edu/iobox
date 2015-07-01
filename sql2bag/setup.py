
#
# Copyright 2015 University of Southern California
# Distributed under the Apache License, Version 2.0. See LICENSE for more info.
#

from distutils.core import setup

setup(
    name="sql2bag",
    description="converts from SQL to CSV by querying a database through an ODBC connection",
    version="0.1-prerelease",
    packages=["sql2bag"],
    package_dir={'sql2bag': 'sql2bag'},
    package_data={'sql2bag': ['example_files/*.*']},
    requires=["pyodbc", "csv", "os", "sys", "datetime", "json", "bagit"],
    maintainer_email="support@misd.isi.edu",
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ])
