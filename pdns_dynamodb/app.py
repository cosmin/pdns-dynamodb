from os import environ
import sys

from boto.dynamodb import connect_to_region
import cli.app

from .backend import Backend
from .frontend import PdnsFrontend

def get_aws_credentials(app):
    access_key=app.params.aws_access_key
    if app.params.aws_secret_key_file:
        with open(app.params.aws_secret_key_file) as f:
            secret_key = f.read().strip()
    else:
        secret_key = app.params.aws_secret_key
    return access_key, secret_key

def exit_with_error(error):
    sys.stderr.write(error)
    sys.exit(1)

def get_dynamodb_connection(app):
    access_key, secret_key = get_aws_credentials(app)
    if not (access_key and secret_key):
        exit_with_error('ERROR: Invalid AWS credentials supplied.')
    connection = connect_to_region(app.params.region,
                                   aws_access_key_id=access_key,
                                   aws_secret_access_key=secret_key)
    if not connection:
        exit_with_error('ERROR: unable to connect, check your region')

    return connection

@cli.app.CommandLineApp
def pdns_backend(app):
    connection = get_dynamodb_connection(app)
    backend = Backend(connection=connection, table_name=app.params.table)
    frontend = PdnsFrontend(sys.stdin, sys.stdout, backend)
    frontend.expect_helo()
    frontend.run()

pdns_backend.add_param("-t", "--table", help="DynamoDB table in which records are stored", required=True, dest="table")
pdns_backend.add_param("-r", "--region", help="AWS region to use", required=True, dest="region")
pdns_backend.add_param("-I", "--access-key-id", help="AWS access key to use (default: $AWS_ACCESS_KEY_ID)",
                       default=environ.get('AWS_ACCESS_KEY_ID'), required=False, dest="aws_access_key")
pdns_backend.add_param("-S", "--secret-key", help="AWS secret key to use (default: $AWS_SECRET_ACCESS_KEY)",
                       default=environ.get('AWS_SECRET_ACCESS_KEY'), required=False, dest="aws_secret_key")
pdns_backend.add_param("-K", "--secret-key-file", help="File containing AWS secret key to use", required=False, dest="aws_secret_key_file")

def run():
    try:
        pdns_backend.run()
    except KeyboardInterrupt:
        # handle C-c gracefully
        pass
