from distutils.core import setup
setup(name='ermrest-iobox',
      version='0.0',
      description='ERMREST IOBox',
      packages=['iobox'],
      package_dir={'': 'src'},
      #package_data={'iobox': ['sql/*.sql']},
      scripts=['bin/ermrest-outbox']
      )
