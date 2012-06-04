from version import __version__

ABI_VERSION = '1'

class PdnsFrontend(object):
    def __init__(self, input_stream, output_stream, backend):
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.backend = backend
        self.logs = []

    def expect_helo(self):
        line = self.readline()
        if not line.startswith('HELO\t'):
            self.fail('invalid HELO line')
            self.readline()
        else:
            _, abi = line.split('\t')
            if abi == ABI_VERSION:
                self.reply('OK\tpdns-dynamodb version %s' % __version__)
            else:
                self.fail('got abi-version %s, expected %s' % (abi, ABI_VERSION))
                self.readline()

    def readline(self):
        return self.input_stream.readline().strip()

    def reply(self, message):
        self.output_stream.write(message)
        self.output_stream.write('\n')
        self.output_stream.flush()

    def log(self, msg):
        self.logs.append(msg)

    def send_logs(self):
        for log in self.logs:
            self.reply('LOG\t%s' % log)
        self.logs = []

    def end(self):
        self.send_logs()
        self.reply('END')

    def fail(self, msg=None):
        self.send_logs()
        if msg:
            self.reply('FAIL\t%s' % msg)
        else:
            self.reply('FAIL')

    def output_record(self, record):
        # DATA qname qclass qtype ttl id content
        msg = '\t'.join(['DATA', record['name'], record['qclass'],
                   record['qtype'], str(record['ttl']), '-1', record['content']])
        self.reply(msg)

    def parse_query(self, line):
        query = line.split("\t")  # Q, qname, qclass, qtype, id, remote-ip-address
        return dict(qname=query[1], qclass=query[2], qtype=query[3])

    def run_one_query(self):
        line = self.readline()
        if not line:
            return
        query = self.parse_query(line)
        if query['qclass'] != 'IN':
            self.log('Class %s not supported' % qclass)
            self.fail()
        else:
            records = self.backend.query(query['qname'], query['qtype'])
            for record in records:
                self.output_record(record)
            self.end()

    def run(self):
        while True:
            self.run_one_query()
