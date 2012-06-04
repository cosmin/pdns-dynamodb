import unittest
from mock import Mock, call
from boto.dynamodb.condition import EQ

from pdns_dynamodb.backend import Backend

class TestBackend(unittest.TestCase):
    def setUp(self):
        self.con = Mock()
        self.table_name = 'SOME_TABLE'
        self.backend = Backend(self.con, self.table_name)

    def test_init_retrieves_the_table(self):
        self.con.get_table.assert_called_once_with(self.table_name)

    def test_query_params_for_ANY_query(self):
        ret = self.backend._query_params_from_query_type('ANY')
        self.assertEqual(ret, {})

    def test_query_params_for_other_queries(self):
        ret = self.backend._query_params_from_query_type('CNAME')
        self.assertEqual(ret, {'range_key_condition':EQ('CNAME')})

    def test_run_regular_query_against_table(self):
        self.backend.table.query.return_value = []
        self.backend.query('example.com', 'NS')
        table = self.backend.table
        table.query.assert_called_once_with('example.com',
                                            range_key_condition=EQ('NS'))

    def test_record_from_value(self):
        name = 'example.com'
        item = {'name': name, 'type':'A', 'ttl': 3600, 'values': ['1.1.1.1']}
        record = self.backend._record_from_value('example.com', item, '1.1.1.1')
        self.assertEqual(record, dict(name=name, qtype='A', qclass='IN',
                                      ttl=3600, content='1.1.1.1'))

    def test_query_builds_records_from_values(self):
        table = self.backend.table
        name = 'example.com'
        item = {'name': name, 'type':'A', 'ttl': 3600, 'values': ['1.1.1.1',
                                                                  '2.2.2.2']}
        table.query.return_value = [item]
        records = self.backend.query(name)
        self.assertEqual(records, [dict(name=name, qtype='A', qclass='IN',
                                      ttl=3600, content='1.1.1.1'),
                                   dict(name=name, qtype='A', qclass='IN',
                                      ttl=3600, content='2.2.2.2')])
