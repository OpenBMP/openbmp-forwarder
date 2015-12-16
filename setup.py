#!/usr/bin/env python

from distutils.core import setup

setup(name='openbmp-forwarder',
      version='0.1.0',
      description='OpenBMP Forwarder',
      author='Tim Evens',
      author_email='tim@openbmp.org',
      url='',
      data_files=[('etc', ['src/etc/openbmp-forwarder.yml'])],
      package_dir={'': 'src/site-packages'},
      packages=['openbmp', 'openbmp.parsed'],
      scripts=['src/bin/openbmp-forwarder']
     )
