from setuptools import setup

from pdns_dynamodb import __version__

setup(name='pdns-dynamodb',
      version=__version__,
      description='PowerDNS backend using DynamoDB',
      author='Cosmin Stejerean',
      author_email='cosmin@offbytwo.com',
      license='Apache License 2.0',
      url='http://github.com/cosmin/pdns-dynamodb',
      packages=['pdns_dynamodb'],
      scripts=['bin/pdns-dynamodb'],
      tests_require=open('test-requirements.txt').readlines(),
      install_requires=open('requirements.txt').readlines(),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Utilities'
        ]
     )
