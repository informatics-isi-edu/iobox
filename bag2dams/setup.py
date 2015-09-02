
#
# Copyright 2015 University of Southern California
# Distributed under the Apache License, Version 2.0. See LICENSE for more info.
#

from distutils.core import setup

setup(
    name="bag2dams",
    description="loads CSV data included in the bag to a DAMS catalog",
    url='https://github.com/informatics-isi-edu/iobox/tree/master/bag2dams',
    author='misd',
    version="0.1-prerelease",
    packages=['bag2dams'],
    package_dir={'bag2dams': 'bag2dams'},
    requires=['sys,'
              'shutil'
              'requests'
              'cookielib'
              'zipfile'
              'urlparse'
              'tarfile'
              'os'
              'tempfile'
              'bagit'
              'simplejson'
              'ordereddict'],
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

