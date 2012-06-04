from boto.dynamodb import connect_to_region
from boto.dynamodb.condition import EQ
from boto.dynamodb.exceptions import DynamoDBKeyNotFoundError

class Backend(object):
    def __init__(self, connection, table_name):
        self.con = connection
        self.table = self.con.get_table(table_name)

    def _query_params_from_query_type(self, query_type):
        if query_type == 'ANY':
            return {}
        else:
            return dict(range_key_condition=EQ(query_type))

    def _record_from_value(self, name, item, value):
        return dict(name=name, qtype=item['type'], qclass='IN',
                    ttl=item['ttl'], content=value)

    def query(self, name, query_type='ANY'):
        records = []
        query_params = self._query_params_from_query_type(query_type)
        for item in self.table.query(name, **query_params):
            for value in item['values']:
                records.append(self._record_from_value(name, item, value))
        return records
