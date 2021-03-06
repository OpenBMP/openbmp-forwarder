#!/usr/bin/env python

from setuptools import setup

setup(name='openbmp-forwarder',
      version='0.1.0',
      description='OpenBMP Forwarder',
      author='Tim Evens',
      author_email='tim@openbmp.org',
      url='',
      data_files=[('etc', ['src/etc/openbmp-forwarder.yml'])],
      package_dir={'openbmp': 'src/site-packages/openbmp', 'openbmp.forwarder': 'src/site-packages/openbmp/forwarder'},
      packages=['openbmp', 'openbmp.forwarder'],
      scripts=['src/bin/openbmp-forwarder']
     )
