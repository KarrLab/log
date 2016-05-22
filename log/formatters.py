from enum import Enum


class TemplateStyle(Enum):
    """
    ``TemplateStyle`` is an enum for controlling template interpolation. ``log`` supports only named
    template variables using only modern interpolation methods.
    """

    PERCENT = '%(param)s'
    BRACES = '{param}'


class Formatter(object):
    """
    ``Formatter`` is a simple wrapper for interpolating log entry templates and context variables.

    >>> template = '[{timestamp}] [{level}] : {message}'
    >>> formatter = Formatter(template, TemplateStyle.BRACES)
    >>> formatter.format_entry({'timestamp': 'now', 'level': 'red alert', 'message': 'ohaii'})
    [now] [red alert] : ohaii
    """

    def __init__(self, template, style, append_new_line=True):
        """
        :param template: the template string for the log message
        :type template: str

        :param style: control value for determining the interpolation method
        :type style: log.formatters.TemplateStyle

        :param append_new_line: should a new line be added to the end of the message
        :type append_new_line: bool
        """
        self.template = template
        if not isinstance(style, TemplateStyle):
            raise ValueError('`style` must be an instance of TemplateStyle')
        self._style = style
        if append_new_line:
            self.template += '\n'

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        if not isinstance(value, TemplateStyle):
            raise ValueError('`style` must be an instance of TemplateStyle')
        self._style = value

    def format_entry(self, params):
        """formats the template with given parameters

        :param params: a dictionary of parameter values for formatting the template
        :type params: dict

        :return: the formatted template
        :rtype: str
        """
        if self.style == TemplateStyle.PERCENT:
            return self.template % params
        return self.template.format(**params)
