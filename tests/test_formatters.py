import unittest

from log.formatters import TemplateStyle, Formatter


class TestFormatter(unittest.TestCase):

    def setUp(self):
        self.template = '[{timestamp}] [{level}] {message}'
        self.style = TemplateStyle.BRACES
        self.formatter = Formatter(self.template, self.style)

    def test_style_getter(self):
        self.assertEqual(self.formatter.style, TemplateStyle.BRACES)

    def test_style_setter_success(self):
        self.formatter.style = TemplateStyle.PERCENT
        self.assertEqual(self.formatter.style, TemplateStyle.PERCENT)

    def test_style_setter_fail(self):
        with self.assertRaises(AssertionError):
            self.formatter.style = 'something else entirely'

    def test_format_entry_success(self):
        params = {'timestamp': 'right_now', 'level': 'boss', 'message': 'hooray!'}
        entry = self.formatter.format_entry(params)
        expected = '[right_now] [boss] hooray!'
        self.assertEqual(entry, expected)

    def test_format_mismatched_formatter(self):
        self.formatter.style = TemplateStyle.PERCENT
        params = {'timestamp': 'right_now', 'level': 'boss', 'message': 'hooray!'}
        entry = self.formatter.format_entry(params)
        expected = self.formatter.template
        self.assertEqual(entry, expected)
