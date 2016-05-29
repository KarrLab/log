import re

from .errors import BadTemplateError, ConfigurationError


class TemplateStyle:
    """
    ``TemplateStyle`` is a handy control workflow for ``Formatter`` to determine how to interpolate templates
    and parameters.

    >>> template = '{timestamp} {level} : {message}'
    >>> fmt_func, style = TemplateStyle.determine_format_style(template)
    >>> fmt_func, style
    TemplateStyle.BRACES, 'braces'
    """

    PERCENT_REGEX = re.compile('%\(\w+\)[a-zA-Z0-9]+')
    BRACES_REGEX = re.compile('\{[\w\.]+\}')

    @staticmethod
    def _fmt_percent(template, **params):
        return template % params

    @staticmethod
    def _fmt_braces(template, **params):
        return template.format(**params)

    PERCENT = _fmt_percent
    BRACES = _fmt_braces

    @classmethod
    def determine_format_style(cls, template):
        """determines the format style of a given template

        :param template: the template to interrogate
        :type template: str

        :returns: the formatting function and style name

        :raises: BadTemplateError
        """
        num_percent = re.findall(cls.PERCENT_REGEX, template)
        num_braces = re.findall(cls.BRACES_REGEX, template)
        if num_percent and not num_braces:
            return cls.PERCENT, 'percent'
        elif num_braces and not num_percent:
            return cls.BRACES, 'braces'
        elif num_percent and num_braces:
            raise BadTemplateError("Mixed string formatting isn't allowed - use only percents or braces")
        else:
            raise BadTemplateError("Couldn't find any matching variable patterns in template")


class Formatter:
    """
    ``Formatter`` is a simple wrapper for interpolating log entry templates and context variables.

    >>> template = '[{timestamp}] [{level}] : {message}'
    >>> formatter = Formatter(template, TemplateStyle.BRACES)
    >>> formatter.format({'timestamp': 'now', 'level': 'red alert', 'message': 'ohaii'})
    [now] [red alert] : ohaii
    """

    PERCENT_KEYS_REGEX = re.compile('%\((?P<key>\w+)\)[a-zA-Z0-9]+')
    BRACES_KEYS_REGEX = re.compile('\{(?P<key>\w+)(\.\w+)?(:>?\w+)?\}')

    def __init__(self, name=None, template=None, append_new_line=True):
        """
        :param name: the name of the formatter
        :type name: str

        :param template: the template to interpolate for the log entry
        :type template: str

        :param append_new_line: should a new line character be appended to the end of the log entry
        :type append_new_line: bool
        """
        self.name = name
        self.append_new_line = append_new_line
        self._setup_template(template)

    def __lt__(self, other):
        return self.name < other.name

    def __le__(self, other):
        return self.name <= other.name

    def __eq__(self, other):
        return self.name == other.name

    def __ge__(self, other):
        return self.name >= other.name

    def __gt__(self, other):
        return self.name >= other.name

    def __hash__(self):
        return super(Formatter, self).__hash__()

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, template):
        self._setup_template(template)

    def format(self, **params):
        """performs the string formatting function appropriate for the template with the given keywords

        :param params: arbitrary keywords to use for string interpolation
        :type params: dict

        :returns: the template formatted with the parameters

        >>> template = '{level} : {message}'
        >>> formatter = Formatter(template=template)
        >>> formatter.format(level='INFO', message='hey there')
        INFO : hey there
        """
        if self._template_format_fnc is None or self._template is None:
            raise ConfigurationError('No template has been set yet')
        message = self._template_format_fnc(self._template, **params)
        if self.append_new_line:
            message = "{}\n".format(message)
        return message

    def extract_template_keys(self):
        """searches the template for iterpolation keys

        :returns: a list of keys

        >>> p_template = '%(message)s'
        >>> p_formatter = Formatter(template=p_template)
        >>> p_formatter.extract_template_keys()
        ['message']
        >>> b_template = '{message} {user.email} {user.name}'
        >>> b_formatter = Formatter(template=b_template)
        >>> b_formatter.extract_template_keys()
        ['message', 'user']
        """
        if self._template_style == 'percent':
            return re.findall(self.PERCENT_KEYS_REGEX, self.template)
        elif self._template_style == 'braces':
            return list(set([g[0] for g in re.findall(self.BRACES_KEYS_REGEX, self.template)]))
        else:
            raise ConfigurationError('No template has been set yet')

    def _setup_template(self, template):
        if template:
            self._template_format_fnc, self._template_style = TemplateStyle.determine_format_style(template)
        else:
            self._template_format_fnc, self._template_style = None, None
        self._template = template
