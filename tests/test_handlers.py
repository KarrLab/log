import codecs
import os
import socket
import subprocess
import sys
import unittest

from log import handlers, levels


class BaseHandlerTest(object):
    def test_write(self):
        raise NotImplementedError


class TestStreamSysOutHandler(BaseHandlerTest, unittest.TestCase):

    def setUp(self):
        self.handler = handlers.StreamHandler(sys.stdout)

    def test_write(self):
        output = 'ohaiii'
        test_dir = os.path.dirname(__file__)
        proj_dir = os.path.dirname(test_dir)
        executable = os.path.join(proj_dir, '.env', 'bin', 'python')
        cmd = 'from log import handlers; ' \
              'import sys; ' \
              'handler = handlers.StreamHandler(sys.stdout); ' \
              'handler.write("{output}")'.format(output=output)
        proc = subprocess.Popen([executable, '-c', cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = proc.communicate()
        expected = bytes('{output}\n'.format(output=output), 'utf8')
        self.assertEqual(stdout, expected)


class TestStreamSysErrHandler(BaseHandlerTest, unittest.TestCase):

    def setUp(self):
        self.handler = handlers.StreamHandler(sys.stderr)

    def test_write(self):
        output = 'ohaiii'
        test_dir = os.path.dirname(__file__)
        proj_dir = os.path.dirname(test_dir)
        executable = os.path.join(proj_dir, '.env', 'bin', 'python')
        cmd = 'from log import handlers; ' \
              'import sys; ' \
              'handler = handlers.StreamHandler(sys.stderr); ' \
              'handler.write("{output}")'.format(output=output)
        proc = subprocess.Popen([executable, '-c', cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderr = proc.communicate()
        expected = bytes('{output}\n'.format(output=output), 'utf8')
        self.assertEqual(stderr, expected)


class TestFileHandler(BaseHandlerTest, unittest.TestCase):

    def setUp(self):
        self.filename = '/tmp/test_handlers.log'
        self.handler = handlers.FileHandler(self.filename)

    def tearDown(self):
        os.remove(self.filename)

    def test_write(self):
        output = 'ohaiii'
        expected = []
        for _ in range(5):
            self.handler.write(output)
            expected.append('{output}\n'.format(output=output))
        with codecs.open(self.filename, 'r', encoding='utf8') as fh:
            contents = [line for line in fh]
        self.assertEqual(contents, expected)


class TestSocketHandler(BaseHandlerTest, unittest.TestCase):

    def setUp(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = ('localhost', 8089)
        # setup socket server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(self.address)
        self.server.listen(5)
        # handler is client
        self.handler = handlers.SocketHandler(self.socket, self.address)

    def tearDown(self):
        del self.server

    def test_write(self):
        output = 'ohaiii'
        self.handler.write(output)
        messages = []
        while True:
            connection, address = self.server.accept()
            buffer = connection.recv(1024)
            if len(buffer) > 0:
                messages.append(buffer)
                break
        expected = [bytes('{output}\n'.format(output=output), 'utf8')]
        self.assertEqual(messages, expected)


class TestSyslogHandler(BaseHandlerTest, unittest.TestCase):

    def setUp(self):
        self.handler = handlers.SysLogHandler()

    def test_write(self):
        self.handler.write('ohaiii', levels.LogLevel.INFO)
