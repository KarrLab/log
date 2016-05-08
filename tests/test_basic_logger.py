import unittest

from log.loggers import Logger


class TestBasicLogger(unittest.TestCase):

    def setUp(self):
        self.logger = Logger()

    def barf(self):
        return 1/0

    def test_debug(self):
        self.logger.debug('this is a debug line')

    def test_info(self):
        self.logger.info('this is an info line')

    def test_warning(self):
        self.logger.warning('this is a warning line')

    def test_error(self):
        self.logger.error('this is an error line')

    def test_exception(self):
        try:
            self.barf()
        except Exception as e:
            self.logger.exception(e)


class TestNamedBasicLogger(TestBasicLogger):

    def setUp(self):
        template = '[{timestamp}] [{name}] [{level}] : {message}'
        self.logger = Logger(name='named-logger', template=template)


class TestExecInfoBasicLogger(TestBasicLogger):
    def setUp(self):
        template = '[{timestamp}] [{name}] [{exec_src}] [{exec_func}] [{exec_line}] [{exec_proc}] [{level}] : {message}'
        self.logger = Logger(name='named-logger', template=template)
