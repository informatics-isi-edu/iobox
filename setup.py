
#
# Copyright 2015 University of Southern California
# Distributed under the Apache License, Version 2.0. See LICENSE for more info.
#

from distutils.core import setup

setup(
    name="iobox",
    description="perform transformations from several data sources to DAMS using data bag elements ",
    url='https://github.com/informatics-isi-edu/iobox/',
    author='misd',
    version="0.1-prerelease",
    packages=['sql2bag','bag2dams'],
    package_dir={'sql2bag': 'sql2bag/sql2bag','bag2dams': 'bag2dams/bag2dams'},
    package_data={'sql2bag': ['gpcr_example/*.*']},
    scripts=['bin/iobox_sql2dams.py'],
    requires=['orderdict','simplejson','pyodbc', 'csv', 'os', 'sys', 'datetime', 'json', 'bagit'],
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

