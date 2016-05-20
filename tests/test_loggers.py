import re
import sys
import unittest

from capturer import CaptureOutput

from log.errors import ConfigurationError
from log.formatters import Formatter, TemplateStyle
from log.handlers import StreamHandler
from log.levels import LogLevel
from log.loggers import Logger


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
        cls.stdout_handler = StreamHandler(sys.stdout)
        cls.stderr_handler = StreamHandler(sys.stderr)

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
