
#
# Copyright 2015 University of Southern California
# Distributed under the Apache License, Version 2.0. See LICENSE for more info.
#

from distutils.core import setup

setup(
    name="dams2bag",
    description="Creates a bag from a set of ERMRest URLs",
    version="0.1-prerelease",
    packages=["dams2bag"],
    package_dir={'dams2bag': 'dams2bag'},
    requires=['sys',
              'cookielib',
              'shutil',
              'os.path',
              'urlparse',
              'requests',
              'csv',
              'bagit',
              'ordereddict',
              'simplejson'],
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
