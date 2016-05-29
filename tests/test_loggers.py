import re
import sys
import unittest
import uuid

from capturer import CaptureOutput

from log import loggers
from log.errors import BadTemplateError, FormatterNotFoundError, ConfigurationError
from log.formatters import Formatter
from log.handlers import StreamHandler
from log.levels import LogLevel
from log.loggers import Logger


DEFAULT_LOG_LINE_REGEX = re.compile('\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}[\+|-]\d{2}:\d{2}\] \[[A-Z]+\] : .*')


class LoggerLoggingMethodsTests:

    def test_debug(self):
        with CaptureOutput() as co:
            self.logger.debug('message')
        co = co.get_text()
        self.assertRegex(co, DEFAULT_LOG_LINE_REGEX)
        self.assertTrue(co.endswith('[DEBUG] : message'))

    def test_info(self):
        with CaptureOutput() as co:
            self.logger.info('message')
        co = co.get_text()
        self.assertRegex(co, DEFAULT_LOG_LINE_REGEX)
        self.assertTrue(co.endswith('[INFO] : message'))

    def test_warning(self):
        with CaptureOutput() as co:
            self.logger.warning('message')
        co = co.get_text()
        self.assertRegex(co, DEFAULT_LOG_LINE_REGEX)
        self.assertTrue(co.endswith('[WARNING] : message'))

    def test_error(self):
        with CaptureOutput() as co:
            self.logger.error('message')
        co = co.get_text()
        self.assertRegex(co, DEFAULT_LOG_LINE_REGEX)
        self.assertTrue(co.endswith('[ERROR] : message'))

    def test_exception(self):
        with CaptureOutput() as co:
            try:
                1 / 0
            except ZeroDivisionError:
                self.logger.exception('message')
        co = co.get_text()
        self.assertRegex(co, DEFAULT_LOG_LINE_REGEX)
        split_co = co.splitlines()
        self.assertTrue(len(split_co) > 1)
        self.assertTrue(split_co[0].endswith('[EXCEPTION] : message'))


class LoggerLoggingMethodsBracesTemplateTests(LoggerLoggingMethodsTests, unittest.TestCase):

    def setUp(self):
        self.logger = Logger('test-logger', LogLevel.DEBUG, timezone='America/Chicago')


class LoggerLoggingMethodsPercentTemplateTests(LoggerLoggingMethodsTests, unittest.TestCase):

    def setUp(self):
        self.logger = Logger('test-logger', LogLevel.DEBUG, timezone='America/Chicago',
            template='[%(timestamp)s] [%(level)s] : %(message)s')


class LoggerPropertiesTests(unittest.TestCase):

    def setUp(self):
        self.logger = Logger('test-logger', LogLevel.DEBUG, timezone='America/Chicago')

    def test_set_default_formatter(self):
        formatter = Formatter(template='{message}', append_new_line=False)
        self.logger.default_formatter = formatter
        new_default_formatter = self.logger.default_formatter
        self.assertEqual(new_default_formatter, formatter)

    def test_get_template(self):
        template = self.logger.template
        self.assertEqual(template, Logger.DEFAULT_TEMPLATE)

    def test_set_template(self):
        new_template = '{message}'
        self.logger.template = new_template
        template = self.logger.template
        self.assertEqual(template, new_template)
        for formatter in self.logger.formatters:
            self.assertEqual(formatter.template, new_template)

    def test_get_timezone(self):
        self.assertEqual(self.logger.timezone, 'America/Chicago')

    def test_set_timezone(self):
        self.logger.timezone = 'America/New York'
        self.assertEqual(self.logger.timezone, 'America/New York')


class LoggerRemoveStuffTests(unittest.TestCase):

    def setUp(self):
        self.logger = Logger()

    def test_remove_formatter(self):
        new_formatter = Formatter()
        self.logger.add_formatter(new_formatter)
        self.logger.remove_formatter(self.logger.default_formatter)
        self.assertEqual(self.logger.formatters, {new_formatter})
        self.assertEqual(self.logger.default_formatter, new_formatter)

    def test_remove_handler(self):
        self.assertEqual(1, len(self.logger.handlers))
        new_handler = StreamHandler(sys.stderr, name='new')
        self.logger.add_handler(new_handler)
        self.assertEqual(2, len(self.logger.handlers))
        rm = [h for h in self.logger.handlers if h.stream == sys.stdout][0]
        self.logger.remove_handler(rm)
        self.assertEqual(1, len(self.logger.handlers))
        self.assertTrue(list(self.logger.handlers)[0].stream == sys.stderr)


class WithLoggerTests(unittest.TestCase):

    def setUp(self):
        self.logger = Logger('test-logger', LogLevel.DEBUG, timezone='America/Chicago')

    def test_using(self):
        formatter = Formatter(name='new', template='check this out: {message}')
        self.logger.add_formatter(formatter)
        self.assertEqual(2, len(self.logger.formatters))

        # default stuff
        with CaptureOutput() as co:
            self.logger.info('message')
        co = co.get_text()
        self.assertRegex(co, DEFAULT_LOG_LINE_REGEX)

        # use name
        with CaptureOutput() as co:
            with self.logger.using('default') as logger:
                logger.info('yay!')
        co = co.get_text()
        self.assertRegex(co, DEFAULT_LOG_LINE_REGEX)

        new_regex = re.compile('check this out: .*')

        # use different name
        with CaptureOutput() as co:
            with self.logger.using('new') as logger:
                logger.info('huzzah!')
        co = co.get_text()
        self.assertRegex(co, new_regex)

        # use instance
        with CaptureOutput() as co:
            with self.logger.using(formatter) as logger:
                logger.info('awwww yeah!')
        co = co.get_text()
        self.assertRegex(co, new_regex)

        # back to normal
        with CaptureOutput() as co:
            self.logger.info('message')
        co = co.get_text()
        self.assertRegex(co, DEFAULT_LOG_LINE_REGEX)

    def test_only(self):
        handler = StreamHandler(sys.stderr)
        self.logger.add_handler(handler)
        self.assertEqual(2, len(self.logger.handlers))

        # normal
        with CaptureOutput() as co:
            self.logger.info('message')
        co = co.get_text()
        split_co = co.splitlines()
        self.assertEqual(2, len(split_co))
        for line in split_co:
            self.assertRegex(line, DEFAULT_LOG_LINE_REGEX)
        self.assertEqual(split_co[0], split_co[1])

        # use default name
        with CaptureOutput() as co:
            with self.logger.only('StreamHandler0') as logger:
                logger.info('there can be only one')
        co = co.get_text()
        split_co = co.splitlines()
        self.assertEqual(1, len(split_co))
        self.assertRegex(co, DEFAULT_LOG_LINE_REGEX)

        # use instance
        with CaptureOutput() as co:
            with self.logger.only(handler) as logger:
                logger.info('again! again!')
        co = co.get_text()
        split_co = co.splitlines()
        self.assertEqual(1, len(split_co))
        self.assertRegex(co, DEFAULT_LOG_LINE_REGEX)

        # back to normal
        with CaptureOutput() as co:
            self.logger.info('message')
        co = co.get_text()
        split_co = co.splitlines()
        self.assertEqual(2, len(split_co))
        for line in split_co:
            self.assertRegex(line, DEFAULT_LOG_LINE_REGEX)
        self.assertEqual(split_co[0], split_co[1])

        # same as normal but showing you can `only` with more than 1
        with CaptureOutput() as co:
            with self.logger.only(handler, 'StreamHandler0') as logger:
                logger.info('again! again!')
        co = co.get_text()
        split_co = co.splitlines()
        self.assertEqual(2, len(split_co))
        for line in split_co:
            self.assertRegex(line, DEFAULT_LOG_LINE_REGEX)
        self.assertEqual(split_co[0], split_co[1])

    def test_using_and_only(self):
        formatter = Formatter(name='new', template='check this out: {message}')
        self.logger.add_formatter(formatter)
        self.assertEqual(2, len(self.logger.formatters))

        handler = StreamHandler(sys.stderr)
        self.logger.add_handler(handler)
        self.assertEqual(2, len(self.logger.handlers))

        with CaptureOutput() as co:
            with self.logger.using(formatter).only(handler) as logger:
                logger.info('pretty neat')
        co = co.get_text()
        split_co = co.splitlines()
        self.assertEqual(1, len(split_co))
        self.assertEqual(co, 'check this out: pretty neat')

    def test_using_unknown_formatter_fails(self):
        with self.assertRaises(FormatterNotFoundError):
            with self.logger.using(Formatter(template='{barf}')) as logger:
                logger.info(barf=True)


class LoggerExtendedFeaturesTests(unittest.TestCase):

    def test_use_all_the_reserved_keys(self):
        template = '{timestamp} | {level} | {name} | {message} | {src} | {line} | {func} | {proc}'
        logger = Logger(template=template)
        logger.info('stuff')

    def test_use_additional_context_static(self):
        logger = Logger(template='{metal} {message}', additional_context={'metal': 'heavy'})
        with CaptureOutput() as co:
            logger.info('message')
        co = co.get_text()
        self.assertEqual(co, 'heavy message')

    def test_use_additional_context_callable(self):
        def _get_uid():
            return str(uuid.uuid4())

        logger = Logger(template='{uid} {message}', additional_context={'uid': _get_uid})
        with CaptureOutput() as co:
            logger.info('message')
        co = co.get_text()
        self.assertRegex(co, '\w{8}-\w{4}-\w{4}-\w{4}-\w{12} message')

    def test_use_write_time_context(self):
        logger = Logger(template='{changeme} {message}')
        with CaptureOutput() as co:
            logger.info('message', changeme='uno')
            logger.info('messages', changeme='dos')
        co = co.get_text().splitlines()
        self.assertEqual(co, ['uno message', 'dos messages'])


class LoggerNoTimezoneSupportTests(unittest.TestCase):

    def test_no_timezone_support_with_timezone_init_fails(self):
        with self.assertRaises(ConfigurationError):
            loggers._arrow_available = False
            Logger(timezone='America/Chicago')


class BadConfigLoggerTests(unittest.TestCase):
    def test_mixed_style_template(self):
        template = '{timestamp} : %(message)s'
        with self.assertRaises(BadTemplateError):
            Logger(template=template)

    def test_no_keys_in_template(self):
        with self.assertRaises(BadTemplateError):
            Logger(template='ohaiiiii')
