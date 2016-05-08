import os
import re
import sys
import traceback
from datetime import datetime

from .formatters import Formatter, TemplateStyle
from .handlers import _HandlerInterface, StreamHandler
from .levels import LogLevel

try:
    import arrow
    _arrow_available = True
except ImportError:
    _arrow_available = False


BRACES_REGEX = re.compile('\{(?P<key>\w+)\}')

PERCENT_REGEX = re.compile('%\((?P<key>\w+)\)\w')


class Logger(object):
    """
    writes log entries
    """

    DEFAULT_NAME = __name__
    DEFAULT_LOG_LEVEL = LogLevel.INFO
    DEFAULT_LOG_TEMPLATE = '[{timestamp}] [{level}] : {message}'
    DEFAULT_LOG_STYLE = TemplateStyle.BRACES
    DEFAULT_FORMATTER_CLASS = Formatter
    DEFAULT_HANDLERS = [StreamHandler(sys.stdout)]
    DEFAULT_TIMEZONE_AWARE = False
    DEFAULT_TIMEZONE = None
    DEFAULT_ADDITIONAL_CONTEXT = {}

    BASE_LOG_PARAMS = ['timestamp', 'level', 'name', 'message', 'exec_src', 'exec_line', 'exec_func', 'exec_proc']

    def __init__(self, name=DEFAULT_NAME, level=DEFAULT_LOG_LEVEL, template=DEFAULT_LOG_TEMPLATE,
                 style=DEFAULT_LOG_STYLE, formatter_class=DEFAULT_FORMATTER_CLASS, handlers=DEFAULT_HANDLERS,
                 timezone_aware=DEFAULT_TIMEZONE_AWARE, timezone=DEFAULT_TIMEZONE,
                 additional_context=DEFAULT_ADDITIONAL_CONTEXT):
        """
        :param name: the name of the logger - defaults to `__name__`
        :type name: str

        :param level: the minimum log level to write - defaults to `log.levels.LogLevel.INFO`
        :type level: log.levels.LogLevel

        :param template: the template used to format the log entries - defaults to `'[{timestamp}] [{level}] : {message}'`
        :type template: str

        :param style: the formatter style to use for the template - defaults to `log.formatters.TemplateStyle.BRACES`
        :type style: log.formatters.TemplateStyle

        :param formatter_class: the class signature of the formatter to be used - defaults to `log.formatters.Formatter`
        :type formatter_class: log.formatters.Formatter

        :param handlers: a list of configured handlers - defaults to `[StreamHandler(sys.stdout)]`
        :type handlers: []

        :param timezone_aware: should timestamps include timezones; requires `arrow` for use - defaults to `False`
        :type timezone_aware: bool

        :param timezone: a timezone string parseable by arrow - defaults to `None`
        :type timezone: str

        :param additional_context: additional key/values to inject into the template that aren't included in RESERVED_LOG_PARAMS
        :type additional_context: dict
        """
        self.name = name or __name__
        self._level = level
        self.additional_context = additional_context

        self.template = template
        assert isinstance(style, TemplateStyle)
        self._style = style
        assert issubclass(formatter_class, Formatter)
        self._formatter_class = formatter_class
        self._formatter = formatter_class(template, style)

        for handler in handlers:
            assert isinstance(handler, _HandlerInterface)
        self._handlers = set(handlers)

        if timezone_aware and not all([timezone, _arrow_available]):
            raise Exception(
                'You must specify a timezone string and have arrow installed to use timezone aware timestamps')
        self._timezone_aware = timezone_aware
        self.timezone = timezone

        self._template_keys = self._extract_template_keys()

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        assert isinstance(value, LogLevel)
        self._level = value

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        assert isinstance(value, TemplateStyle)
        self._style = value
        self._formatter = self.formatter_class(self.template, self._style)

    @property
    def formatter_class(self):
        return self._formatter_class

    @formatter_class.setter
    def formatter_class(self, value):
        assert issubclass(value, Formatter)
        self._formatter_class = value
        self._formatter = self.formatter_class(self.template, self._style)

    @property
    def timezone_aware(self):
        return self._timezone_aware

    @timezone_aware.setter
    def timezone_aware(self, value):
        if value and not all([self.timezone, _arrow_available]):
            raise Exception(
                'You must specify a timezone string and have arrow installed to use timezone aware timestamps')
        self._timezone_aware = value

    @property
    def formatter(self):
        return self._formatter

    @property
    def handlers(self):
        return list(self._handlers)

    def add_handler(self, handler):
        """adds a new handler to the list of handlers

        :param handler: a new handler to log out entries
        :type handler: log.handlers._HandlerInterface
        """
        assert isinstance(handler, _HandlerInterface)
        self._handlers.add(handler)

    def remove_handler(self, handler):
        """removes a handler from the list of handlers

        :param handler: the handler to be removed
        :type handler: log.handlers._HandlerInterface
        """
        self._handlers.remove(handler)

    def _extract_template_keys(self):
        """ extracts all keys from the log entry template """
        if self._style is TemplateStyle.BRACES:
            return BRACES_REGEX.findall(self.template)
        return PERCENT_REGEX.findall(self.template)

    def _log(self, message, level, exception=None, **kwargs):
        """formats the message and writes it out via the handlers

        :param message: the information to be logged
        :type message: str

        :param level: the level of the log message
        :type level: log.levels.LogLevel

        :param kwargs: arbitrary key/values to inject into the template at write time
        :type kwargs: dict
        """
        params = {'message': message, 'level': level, 'name': self.name}
        # set the timestamp if it is in the template
        if 'timestamp' in self._template_keys:
            if self._timezone_aware:
                params['timestamp'] = arrow.utcnow().to(self.timezone).isoformat()
            else:
                params['timestamp'] = datetime.now().isoformat()
        # set the execution params if they are in the template
        if {'exec_src', 'exec_line', 'exec_func', 'exec_proc'}.intersection(set(self._template_keys)):
            frame = sys._getframe(2)
            params['exec_src'] = frame.f_code.co_filename
            params['exec_func'] = frame.f_code.co_name
            params['exec_line'] = frame.f_lineno
            params['exec_proc'] = os.getpid()
        # set the message to the exception info if it's an exception
        if exception:
            params['message'] = '{}\n'.format(message) + '\n'.join(traceback.format_exc().splitlines())
        # inject configured additional context info
        for key, value in self.additional_context.items():
            if type(value) == type(lambda x: ()):  # check if it's callable
                params[key] = value()
            else:
                params[key] = value
        # inject instance context info
        for key, value in kwargs.items():
            params[key] = value
        # format and handle the line
        log_line = self._formatter.format_entry(params)
        for handler in self._handlers:
            handler.write(log_line)

    def debug(self, message, **kwargs):
        """writes a debug line

        :param message: the message to log out
        :type message: str

        :param kwargs: arbitrary key/values to inject into the template at write time
        :type kwargs: dict
        """
        if self._level <= LogLevel.DEBUG:
            self._log(message, LogLevel.DEBUG, **kwargs)

    def info(self, message, **kwargs):
        """writes an info line

        :param message: the message to log out
        :type message: str

        :param kwargs: arbitrary key/values to inject into the template at write time
        :type kwargs: dict
        """
        if self._level <= LogLevel.INFO:
            self._log(message, LogLevel.INFO, **kwargs)

    def warning(self, message, **kwargs):
        """writes a warning line

        :param message: the message to log out
        :type message: str

        :param kwargs: arbitrary key/values to inject into the template at write time
        :type kwargs: dict
        """
        if self._level <= LogLevel.WARNING:
            self._log(message, LogLevel.WARNING, **kwargs)

    def error(self, message, **kwargs):
        """writes an error line

        :param message: the message to log out
        :type message: str

        :param kwargs: arbitrary key/values to inject into the template at write time
        :type kwargs: dict
        """
        self._log(message, LogLevel.ERROR, **kwargs)

    def exception(self, exception):
        """writes an exception string and stack trace

        :param exception: a raised exception
        :type exception: Exception
        """
        self._log(message='', level=LogLevel.EXCEPTION, exception=exception)
