import syslog
import unittest

from log.levels import LogLevel


class TestLogLevel(unittest.TestCase):

    def test_order(self):
        self.assertTrue(LogLevel.DEBUG < LogLevel.INFO < LogLevel.WARNING < LogLevel.ERROR < LogLevel.EXCEPTION)

    def test_syslog_eq(self):
        self.assertEqual(LogLevel.DEBUG.syslog_eq, syslog.LOG_DEBUG)
        self.assertEqual(LogLevel.INFO.syslog_eq, syslog.LOG_INFO)
        self.assertEqual(LogLevel.WARNING.syslog_eq, syslog.LOG_WARNING)
        self.assertEqual(LogLevel.ERROR.syslog_eq, syslog.LOG_ERR)
        self.assertEqual(LogLevel.EXCEPTION.syslog_eq, syslog.LOG_ERR)
