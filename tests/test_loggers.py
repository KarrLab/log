import re
import sys
import unittest
import uuid

from capturer import CaptureOutput

from log import Logger
from log.errors import ConfigurationError
from log.formatters import Formatter, TemplateStyle
from log.handlers import StreamHandler
from log.levels import LogLevel


class SimpleLoggerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = Logger(level=LogLevel.DEBUG)
        cls.log_regex = re.compile('\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\] \[\w+\] : .*')

    def test_debug(self):
        output = 'too much'
        with CaptureOutput() as captured:
            self.logger.debug(output)
        capd = captured.get_text()
        self.assertRegex(capd, self.log_regex)
        self.assertTrue(capd.endswith('[DEBUG] : {output}'.format(output=output)))

    def test_info(self):
        output = 'ohaiii'
        with CaptureOutput() as captured:
            self.logger.info(output)
        capd = captured.get_text()
        self.assertRegex(capd, self.log_regex)
        self.assertTrue(capd.endswith('[INFO] : {output}'.format(output=output)))

    def test_warning(self):
        output = 'booooo'
        with CaptureOutput() as captured:
            self.logger.warning(output)
        capd = captured.get_text()
        self.assertRegex(capd, self.log_regex)
        self.assertTrue(capd.endswith('[WARNING] : {output}'.format(output=output)))

    def test_error(self):
        output = 'nooope'
        with CaptureOutput() as captured:
            self.logger.error(output)
        capd = captured.get_text()
        self.assertRegex(capd, self.log_regex)
        self.assertTrue(capd.endswith('[ERROR] : {output}'.format(output=output)))

    def test_exception(self):
        with CaptureOutput() as captured:
            try:
                1 / 0
            except ZeroDivisionError as e:
                self.logger.exception(e)
        capd = captured.get_lines()
        self.assertRegex(capd[0], self.log_regex)
        self.assertEqual(capd[-1], 'ZeroDivisionError: division by zero')


class TimezoneAwareLoggerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = Logger(timezone_aware=True, timezone='America/Chicago')
        cls.log_regex = re.compile('\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}-05:00\] \[\w+\] : .*')

    def test_info(self):
        output = 'ohaiii'
        with CaptureOutput() as captured:
            self.logger.info(output)
        capd = captured.get_text()
        self.assertRegex(capd, self.log_regex)
        self.assertTrue(capd.endswith('[INFO] : {output}'.format(output=output)))

    def test_setup_without_timezone(self):
        with self.assertRaises(ConfigurationError):
            Logger(timezone_aware=True)

    def test_is_timezone_aware(self):
        self.assertTrue(self.logger.is_timezone_aware)
        logger = Logger()
        self.assertFalse(logger.is_timezone_aware)

    def test_make_timezone_aware(self):
        logger = Logger()
        self.assertFalse(logger.is_timezone_aware)
        logger.make_timezone_aware('America/Chicago')
        self.assertTrue(self.logger.is_timezone_aware)

    def test_remove_timezone(self):
        self.assertTrue(self.logger.is_timezone_aware)
        self.logger.remove_timezone()
        self.assertFalse(self.logger.is_timezone_aware)

    def test_get_timestamp(self):
        ts = self.logger._get_timestamp()
        self.assertRegex(ts, '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}-05:00')

    def test_get_exec_info(self):
        # need to flub this a little
        def get_info():
            exec_info = self.logger._get_exec_info()
            return exec_info
        exec_info = get_info()
        self.assertTrue(exec_info['exec_src'].endswith('test_loggers.py'))  # this file name
        self.assertTrue(exec_info['exec_line'])  # just assert it's a positive integer - this could get ugly to maintain
        self.assertEqual(exec_info['exec_func'], 'test_get_exec_info')  # this function's name
        self.assertTrue(exec_info['exec_proc'])  # just assert it's a positive integer


class GetterSetterLoggerTests(unittest.TestCase):

    def setUp(self):
        self.logger = Logger()

    def test_get_level(self):
        self.assertEqual(self.logger.level, LogLevel.INFO)

    def test_set_level(self):
        self.logger.info('stuff')
        self.logger.level = LogLevel.WARNING
        with CaptureOutput() as captured:
            self.logger.info('this should not show up')
        capd = captured.get_text()
        self.assertEqual(capd, '')

    def test_set_level_error(self):
        with self.assertRaises(AssertionError):
            self.logger.level = 'unknown'

    def test_get_formatter_class(self):
        self.assertEqual(self.logger.formatter_class, Formatter)

    def test_get_formatter(self):
        class DerpFormatter(Formatter):
            pass
        logger = Logger(formatter_class=DerpFormatter)
        derp = DerpFormatter(Logger.DEFAULT_LOG_TEMPLATE, TemplateStyle.BRACES)
        self.assertEqual(logger.formatter.template, derp.template)

    def test_set_formatter(self):
        formatter = Formatter('{message}', TemplateStyle.BRACES)
        self.logger.formatter = formatter
        message = 'yay simple'
        with CaptureOutput() as captured:
            self.logger.info(message)
        capd = captured.get_text()
        self.assertEqual(capd, message)

    def test_get_handlers(self):
        handlers = self.logger.handlers
        self.assertEqual(1, len(handlers))
        handler = handlers[0]
        self.assertIsInstance(handler, StreamHandler)


class MultiHandlerLoggerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.stdout_handler = StreamHandler('test:sys.stdout', sys.stdout)
        cls.stderr_handler = StreamHandler('test:sys.stderr', sys.stderr)

    def test_add_handler(self):
        logger = Logger(handlers=[self.stdout_handler], template='{message}')
        message = 'simple'
        with CaptureOutput() as captured:
            logger.info(message)
        capd = captured.get_text()
        self.assertEqual(capd, message)
        logger.add_handler(self.stderr_handler)
        self.assertEqual(set(logger.handlers), {self.stdout_handler, self.stderr_handler})
        with CaptureOutput() as captured:
            logger.info(message)
        capd = captured.get_lines()
        self.assertEqual(2, len(capd))
        self.assertEqual(capd[0], capd[1])

    def test_remove_handler(self):
        logger = Logger(handlers=[self.stdout_handler], template='%(message)s', style=TemplateStyle.PERCENT)
        message = 'simple'
        with CaptureOutput() as captured:
            logger.info(message)
        capd = captured.get_text()
        self.assertEqual(capd, message)
        logger.add_handler(self.stderr_handler)
        self.assertEqual(set(logger.handlers), {self.stdout_handler, self.stderr_handler})
        with CaptureOutput() as captured:
            logger.info(message)
        capd = captured.get_lines()
        self.assertEqual(2, len(capd))
        self.assertEqual(capd[0], capd[1])
        logger.remove_handler(self.stderr_handler)
        self.assertEqual(logger.handlers, [self.stdout_handler])


class AdditionalContextLoggerTests(unittest.TestCase):

    @staticmethod
    def get_unique_id():
        return 'this-is-your-super-special-uid'

    @classmethod
    def setUpClass(cls):
        template = '{uid} : {message}'
        cls.logger = Logger(template=template, additional_context={'uid': cls.get_unique_id})

    def test_additional_context_in_log(self):
        message = 'hooray!!!'
        with CaptureOutput() as captured:
            self.logger.info(message)
        capd = captured.get_text().rstrip()
        self.assertEqual(capd, 'this-is-your-super-special-uid : hooray!!!')
        with CaptureOutput() as captured:
            self.logger.info(message)
        capd = captured.get_text().rstrip()
        self.assertEqual(capd, 'this-is-your-super-special-uid : hooray!!!')


class KwargsContextLoggerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        template = '{uid} : {message}'
        cls.logger = Logger(template=template)

    def test_kwargs_show_up_in_log(self):
        with CaptureOutput() as captured:
            self.logger.info('message', uid='set-on-runtime')
        capd = captured.get_text()
        self.assertEqual(capd, 'set-on-runtime : message')

        with CaptureOutput() as captured:
            self.logger.info('message', uid='set-again-on-runtime')
        capd = captured.get_text()
        self.assertEqual(capd, 'set-again-on-runtime : message')

        with CaptureOutput() as captured:
            self.logger.info('message', uid=str(uuid.uuid4()))
        capd = captured.get_text()
        self.assertRegex(capd, '\w{8}-\w{4}-\w{4}-\w{4}-\w{12} : message')
