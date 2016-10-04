import codecs
import six
from six import StringIO as PortableStringIO
import os
import socket
import sys
import unittest

from log import handlers


class BaseHandlerTest(object):
    def test_write(self):
        raise NotImplementedError


class StreamHandlerTests(BaseHandlerTest, unittest.TestCase):
    def setUp(self):
        self.handler = handlers.StreamHandler(sys.stdout)

    def test_write(self):
        stream = PortableStringIO()
        handler = handlers.StreamHandler(stream=stream)
        handler.write('ohaiii')
        stream.seek(0)
        output = stream.getvalue()
        self.assertEqual(output, 'ohaiii')


class FileHandlerTests(BaseHandlerTest, unittest.TestCase):

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
        if six.PY3:
            expected = [bytes('{output}'.format(output=output), 'utf8')]
        else:
            expected = ['{output}'.format(output=output)]
        self.assertEqual(messages, expected)


class HandlerCompTests(unittest.TestCase):

    def test_order(self):
        h0 = handlers._HandlerInterface(name='h0')
        h1 = handlers._HandlerInterface(name='h1')
        h2 = handlers._HandlerInterface(name='h2')
        h1a = handlers._HandlerInterface(name='h1')
        self.assertTrue(h0 < h1 <= h1a < h2 > h1 >= h1a > h0)
        self.assertEqual(h1, h1a)
        handler_set0 = {h2, h1, h0, h1a}
        handler_set1 = {h1, h0, h1a, h2}
        self.assertEqual(handler_set0, handler_set1)
