from os import environ
import sys

from boto.dynamodb import connect_to_region

from .backend import Backend
from .frontend import PdnsFrontend

def get_aws_credentials(params):
    access_key=params.get('--access-key-id') or environ.get('AWS_ACCESS_KEY_ID')
    if params.get('--secret-key-file'):
        with open(params.get('--secret-key-file')) as f:
            secret_key = f.read().strip()
    else:
        secret_key = params.get('--secret-key-id') or environ.get('AWS_SECRET_ACCESS_KEY')
    return access_key, secret_key

def exit_with_error(error):
    sys.stderr.write(error)
    sys.exit(1)

def get_dynamodb_connection(params):
    region = params['--region']
    access_key, secret_key = get_aws_credentials(params)
    if not (access_key and secret_key):
        exit_with_error('ERROR: Invalid AWS credentials supplied.')
    connection = connect_to_region(region,
                                   aws_access_key_id=access_key,
                                   aws_secret_access_key=secret_key)
    if not connection:
        exit_with_error('ERROR: unable to connect, check your region')

    return connection

def run(params):
    connection = get_dynamodb_connection(params)
    backend = Backend(connection=connection, table_name=params['--table'])
    frontend = PdnsFrontend(sys.stdin, sys.stdout, backend)
    frontend.expect_helo()
    frontend.run()
