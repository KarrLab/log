import unittest

from log.levels import LogLevel


class LogLevelTests(unittest.TestCase):

    def test_order(self):
        self.assertTrue(LogLevel.DEBUG < LogLevel.INFO < LogLevel.WARNING < LogLevel.ERROR < LogLevel.EXCEPTION)

    def test_str(self):
        self.assertEqual('DEBUG', str(LogLevel.DEBUG))
        self.assertEqual('INFO', str(LogLevel.INFO))
        self.assertEqual('WARNING', str(LogLevel.WARNING))
        self.assertEqual('ERROR', str(LogLevel.ERROR))
        self.assertEqual('EXCEPTION', str(LogLevel.EXCEPTION))

    def test_gt(self):
        self.assertGreater(LogLevel.EXCEPTION, LogLevel.ERROR)
        self.assertGreater(LogLevel.ERROR, LogLevel.WARNING)
        self.assertGreater(LogLevel.WARNING, LogLevel.INFO)
        self.assertGreater(LogLevel.INFO, LogLevel.DEBUG)

    def test_ge(self):
        self.assertGreaterEqual(LogLevel.EXCEPTION, LogLevel.ERROR)
        self.assertGreaterEqual(LogLevel.ERROR, LogLevel.WARNING)
        self.assertGreaterEqual(LogLevel.WARNING, LogLevel.INFO)
        self.assertGreaterEqual(LogLevel.INFO, LogLevel.DEBUG)
        self.assertGreaterEqual(LogLevel.DEBUG, LogLevel.DEBUG)

    def test_eq(self):
        self.assertNotEqual(LogLevel.EXCEPTION, LogLevel.ERROR)
        self.assertNotEqual(LogLevel.ERROR, LogLevel.WARNING)
        self.assertNotEqual(LogLevel.WARNING, LogLevel.INFO)
        self.assertNotEqual(LogLevel.INFO, LogLevel.DEBUG)
        self.assertEqual(LogLevel.DEBUG, LogLevel.DEBUG)

    def test_le(self):
        self.assertLessEqual(LogLevel.DEBUG, LogLevel.DEBUG)
        self.assertLessEqual(LogLevel.DEBUG, LogLevel.INFO)
        self.assertLessEqual(LogLevel.INFO, LogLevel.WARNING)
        self.assertLessEqual(LogLevel.WARNING, LogLevel.ERROR)
        self.assertLessEqual(LogLevel.ERROR, LogLevel.EXCEPTION)

    def test_lt(self):
        self.assertLess(LogLevel.DEBUG, LogLevel.INFO)
        self.assertLess(LogLevel.INFO, LogLevel.WARNING)
        self.assertLess(LogLevel.WARNING, LogLevel.ERROR)
        self.assertLess(LogLevel.ERROR, LogLevel.EXCEPTION)
