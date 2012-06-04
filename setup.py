from setuptools import setup

from pdns_dynamodb.version import __version__

setup(name='pdns-dynamodb',
      version=__version__,
      description='PowerDNS backend using DynamoDB',
      author='Cosmin Stejerean',
      author_email='cosmin@offbytwo.com',
      license='Apache License 2.0',
      url='http://github.com/cosmin/pdns-dynamodb',
      packages=['pdns_dynamodb'],
      scripts=['bin/pdns-dynamodb'],
      install_requires=open('requirements.txt').readlines()
     )
