import unittest

from log.errors import BadTemplateError, ConfigurationError
from log.formatters import TemplateStyle, Formatter


class TemplateStyleTests(unittest.TestCase):

    def test_determine_format_style_percent(self):
        template = '%(timestamp)s | %(level)s : %(message)s'
        style, name = TemplateStyle.determine_format_style(template)
        self.assertEqual(style, TemplateStyle.PERCENT)
        self.assertEqual(name, 'percent')

    def test_determine_format_style_braces(self):
        template = '{timestamp} | {level} : {message}'
        style, name = TemplateStyle.determine_format_style(template)
        self.assertEqual(style, TemplateStyle.BRACES)
        self.assertEqual(name, 'braces')

    def test_determine_format_style_mixed_fails(self):
        template = '{timestamp} | {level} : %(message)s'
        with self.assertRaises(BadTemplateError):
            TemplateStyle.determine_format_style(template)

    def test_determine_format_style_no_keys_fails(self):
        template = 'nada'
        with self.assertRaises(BadTemplateError):
            TemplateStyle.determine_format_style(template)

    def test_fmt_percent(self):
        template = "The name's %(lname)s, %(fname)s %(lname)s."
        params = {'lname': 'Bond', 'fname': 'James'}
        output = TemplateStyle.PERCENT(template, **params)
        self.assertEqual(output, "The name's Bond, James Bond.")

    def test_fmt_braces(self):
        template = "The name's {lname}, {fname} {lname}."
        params = {'lname': 'Bond', 'fname': 'James'}
        output = TemplateStyle.BRACES(template, **params)
        self.assertEqual(output, "The name's Bond, James Bond.")


class FormatterTests(unittest.TestCase):

    def setUp(self):
        self.formatter = Formatter(template='{level} {message}')

    def test_order(self):
        f0 = Formatter(name='formatter0')
        f1 = Formatter(name='formatter1')
        f2 = Formatter(name='formatter2')
        f1a = Formatter(name='formatter1')
        self.assertTrue(f0 < f1 <= f1a < f2 > f1 >= f1a > f0)
        self.assertEqual(f1, f1a)
        formatter_set1 = {f2, f1a, f0, f1}
        formatter_set2 = {f1a, f0, f1, f2}
        self.assertEqual(formatter_set1, formatter_set2)

    def test_get_template(self):
        self.assertEqual(self.formatter.template, '{level} {message}')

    def test_set_template(self):
        self.formatter.template = '{message} {level}'
        self.assertEqual(self.formatter.template, '{message} {level}')

    def test_format(self):
        params = {'level': 'sea', 'message': 'lost at'}
        output = self.formatter.format(**params)
        self.assertEqual(output, 'sea lost at\n')

    def test_format_no_append_line(self):
        formatter = Formatter(template='{message} {level}', append_new_line=False)
        params = {'level': 'sea', 'message': 'lost at'}
        output = formatter.format(**params)
        self.assertEqual(output, 'lost at sea')

    def test_format_no_template_fails(self):
        formatter = Formatter()
        with self.assertRaises(ConfigurationError):
            formatter.format(fail=True)

    def test_extract_template_keys_percent(self):
        formatter = Formatter(template='%(writing)s %(tests)s %(sucks)s')
        keys = formatter.extract_template_keys()
        self.assertEqual(set(keys), {'writing', 'tests', 'sucks'})

    def test_extract_template_keys_braces(self):
        formatter = Formatter(template='{level} {message} {person.f_name:>12} {person.l_lname:>12} {person.age:03d}')
        keys = formatter.extract_template_keys()
        self.assertEqual(set(keys), {'level', 'message', 'person'})

    def test_extract_template_keys_no_template_fails(self):
        formatter = Formatter()
        with self.assertRaises(ConfigurationError):
            formatter.extract_template_keys()
