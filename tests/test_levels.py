import unittest

from log.levels import LogLevel


class LogLevelTests(unittest.TestCase):

    def test_order(self):
        self.assertTrue(LogLevel.DEBUG < LogLevel.INFO < LogLevel.WARNING < LogLevel.ERROR < LogLevel.EXCEPTION)
        self.assertTrue(LogLevel.EXCEPTION > LogLevel.ERROR > LogLevel.WARNING > LogLevel.INFO > LogLevel.DEBUG)
        self.assertTrue(LogLevel.DEBUG <= LogLevel.INFO <= LogLevel.WARNING <= LogLevel.ERROR <= LogLevel.EXCEPTION)
        self.assertTrue(LogLevel.EXCEPTION >= LogLevel.ERROR >= LogLevel.WARNING >= LogLevel.INFO >= LogLevel.DEBUG)
        self.assertTrue(LogLevel.EXCEPTION != LogLevel.ERROR != LogLevel.WARNING != LogLevel.INFO != LogLevel.DEBUG)

    def test_str(self):
        self.assertEqual('DEBUG', str(LogLevel.DEBUG))
        self.assertEqual('INFO', str(LogLevel.INFO))
        self.assertEqual('WARNING', str(LogLevel.WARNING))
        self.assertEqual('ERROR', str(LogLevel.ERROR))
        self.assertEqual('EXCEPTION', str(LogLevel.EXCEPTION))
