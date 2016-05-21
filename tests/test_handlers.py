import codecs
import os
import socket
import subprocess
import sys
import unittest

from log import handlers


class BaseHandlerTest(object):
    def test_write(self):
        raise NotImplementedError


# using popen to test stdout/err tests because we want to ensure messages are being sent to the right system io
# using capturer (like in logger tests) combines out and err and is pretty unhelpful here

class StreamSysOutHandlerTests(BaseHandlerTest, unittest.TestCase):

    def setUp(self):
        self.handler = handlers.StreamHandler('test:sys.stdout', sys.stdout)

    def test_write(self):
        output = 'ohaiii'
        cmd = 'from log import handlers; ' \
              'import sys; ' \
              'handler = handlers.StreamHandler("test:sys.stdout", sys.stdout); ' \
              'handler.write("{output}")'.format(output=output)
        proc = subprocess.Popen(['python', '-c', cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = proc.communicate()
        expected = bytes('{output}'.format(output=output), 'utf8')
        self.assertEqual(stdout, expected)


class StreamSysErrHandlerTests(BaseHandlerTest, unittest.TestCase):

    def setUp(self):
        self.handler = handlers.StreamHandler('test:sys.stderr', sys.stderr)

    def test_write(self):
        output = 'ohaiii'
        cmd = 'from log import handlers; ' \
              'import sys; ' \
              'handler = handlers.StreamHandler("test:sys.stderr", sys.stderr); ' \
              'handler.write("{output}")'.format(output=output)
        proc = subprocess.Popen(['python', '-c', cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderr = proc.communicate()
        expected = bytes('{output}'.format(output=output), 'utf8')
        self.assertEqual(stderr, expected)


class FileHandlerTests(BaseHandlerTest, unittest.TestCase):

    def setUp(self):
        self.filename = '/tmp/test_handlers.log'
        self.handler = handlers.FileHandler('test:fh', self.filename)

    def tearDown(self):
        os.remove(self.filename)

    def test_write(self):
        output = 'ohaiii'
        expected = []
        for _ in range(5):
            self.handler.write(output)
            expected.append('{output}'.format(output=output))
        expected = [''.join(expected)]
        with codecs.open(self.filename, 'r', encoding='utf8') as fh:
            contents = [line for line in fh]
        self.assertEqual(contents, expected)


class SocketHandlerTests(BaseHandlerTest, unittest.TestCase):

    def setUp(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = ('localhost', 8089)
        # setup socket server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(self.address)
        self.server.listen(5)
        # handler is a client
        self.handler = handlers.SocketHandler('test:localhost@8089', self.socket, self.address)

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
        expected = [bytes('{output}'.format(output=output), 'utf8')]
        self.assertEqual(messages, expected)
