from enum import Enum


class TemplateStyle(Enum):
    """
    message template interpolation controls
    """

    PERCENT = '%(param)s'
    BRACES = '{param}'


class Formatter(object):
    """
    a simple wrapper for interpolating message strings
    """

    def __init__(self, template, style):
        """
        :param template: the template string for the log message
        :type template: str

        :param style: control value for determining the interpolation method
        :type style: log.formatters.TemplateStyle
        """
        self.template = template
        assert isinstance(style, TemplateStyle)
        self._style = style

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        assert isinstance(value, TemplateStyle)
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
