import unittest
from mock import Mock, call

from pdns_dynamodb.frontend import *
from pdns_dynamodb.version import __version__

class TestFrontend(unittest.TestCase):
    def setUp(self):
        self.input = Mock()
        self.output = Mock()
        self.backend = Mock()
        self.frontend = PdnsFrontend(self.input, self.output, self.backend)

    def assert_reply(self, expected):
        self.assert_replies(expected)

    def assert_replies(self, *replies):
        expected = []
        for reply in replies:
            expected.append(call(reply))
            expected.append(call('\n'))
        self.output.write.assert_has_calls(expected)

    def test_unsupported_abi(self):
        self.input.readline.return_value = 'HELO\t0'
        self.frontend.expect_helo()
        self.assert_reply('FAIL\tgot abi-version 0, expected 1')

    def test_invalid_helo(self):
        self.input.readline.return_value = 'JUNK'
        self.frontend.expect_helo()
        self.assert_reply('FAIL\tinvalid HELO line')

    def test_valid_helo(self):
        self.input.readline.return_value = 'HELO\t1'
        self.frontend.expect_helo()
        self.assert_reply('OK\tpdns-dynamodb version %s' % __version__)

    def test_parsing_the_query(self):
        data = self.frontend.parse_query('Q\texample.com\tIN\tANY\t-1\t0.0.0.0')
        self.assertEqual(data['qname'], 'example.com')
        self.assertEqual(data['qclass'], 'IN')
        self.assertEqual(data['qtype'], 'ANY')

    def test_output_record(self):
        record = dict(name='example.com', qclass='IN', qtype='A',
                      ttl=3600, content='1.1.1.1')
        self.frontend.output_record(record)
        self.assert_reply('DATA\texample.com\tIN\tA\t3600\t-1\t1.1.1.1')

    def test_run_one_query(self):
        self.input.readline.return_value = 'Q\texample.com\tIN\tANY\t-1\t0.0.0.0'
        records = [dict(name='example.com', qclass='IN', qtype='A',
                       ttl=3600, content='1.1.1.1'),
                   dict(name='example.com', qclass='IN', qtype='NS',
                        ttl=4800, content='ns1.example.com')]
        self.backend.query.return_value = records
        self.frontend.log('hello, world')
        self.frontend.run_one_query()
        self.backend.query.callend_once_with('example.com', 'ANY')
        self.assert_replies('DATA\texample.com\tIN\tA\t3600\t-1\t1.1.1.1',
                            'DATA\texample.com\tIN\tNS\t4800\t-1\tns1.example.com',
                            'LOG\thello, world',
                            'END')
