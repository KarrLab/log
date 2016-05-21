import inspect
import os
import re
import sys
import traceback
from datetime import datetime

from .errors import ConfigurationError
from .formatters import Formatter, TemplateStyle
from .handlers import _HandlerInterface, StreamHandler
from .levels import LogLevel

try:
    import arrow
    _arrow_available = True
except ImportError:  # pragma: no cover
    _arrow_available = False  # pragma: no cover


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
    DEFAULT_HANDLERS = [StreamHandler(name='default:sys.stdout', stream=sys.stdout)]
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

        :param template: the template used to format the log entries -
            defaults to `'[{timestamp}] [{level}] : {message}'`
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

        :param additional_context: additional key/values to inject into the template that aren't
            included in RESERVED_LOG_PARAMS
        :type additional_context: dict
        """
        self.name = name
        self.additional_context = additional_context

        if not isinstance(level, LogLevel):
            raise ValueError('`level` must be an instance of LogLevel')
        self._level = level

        self.template = template
        if not isinstance(style, TemplateStyle):
            raise ValueError('`style` must be an instance of TemplateStyle')

        self._style = style
        if not issubclass(formatter_class, Formatter):
            raise TypeError('`formatter_class` must be one or subclass of Formatter')
        self._formatter = formatter_class(template, style)

        self._handlers = []
        for i, handler in enumerate(handlers):
            if not isinstance(handler, _HandlerInterface):
                raise ValueError('`handlers[{i}]` does not implement _HandlerInterface'.format(i=i))
            if handler.name not in [h.name for h in self._handlers]:
                self._handlers.append(handler)

        if timezone:
            self.timezone = timezone
            self._timezone_aware = True
        elif timezone_aware and not timezone:
            self.timezone = 'UTC'
            self._timezone_aware = True
        elif timezone_aware or timezone and not _arrow_available:
            raise ConfigurationError(
                'To use timezone aware timestamps you must install the [timestamp] extras and specify a '
                'timezone or set timezone_aware true')
        else:
            self._timezone_aware = False
            self.timezone = None

        self._template_keys = self._extract_template_keys()

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        assert isinstance(level, LogLevel)
        self._level = level

    @property
    def formatter_class(self):
        return self._formatter.__class__

    @property
    def formatter(self):
        return self._formatter

    @formatter.setter
    def formatter(self, formatter):
        assert isinstance(formatter, Formatter)
        self._formatter = formatter

    @property
    def handlers(self):
        return self._handlers

    @property
    def is_timezone_aware(self):
        return self._timezone_aware

    def make_timezone_aware(self, timezone):
        if not _arrow_available:
            raise ConfigurationError(
                'To use timezone aware timestamps you must install the [timestamp] extras and specify a timezone')
        self._timezone_aware = True
        self.timezone = timezone

    def remove_timezone(self):
        self._timezone_aware = False
        self.timezone = None

    def add_handler(self, handler):
        """adds a new handler to the list of handlers

        :param handler: a new handler to log out entries
        :type handler: log.handlers._HandlerInterface
        """
        if not isinstance(handler, _HandlerInterface):
            raise ValueError('`handler` does not implement _HandlerInterface')
        if handler.name not in [h.name for h in self._handlers]:
            self._handlers.append(handler)

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

    def _log(self, message, level, exception=None, **kwargs):  # pragma: no cover
        """formats the message and writes it out via the handlers

        :param message: the information to be logged
        :type message: str

        :param level: the level of the log message
        :type level: log.levels.LogLevel

        :param kwargs: arbitrary key/values to inject into the template at write time
        :type kwargs: dict
        """
        params = {'message': message, 'level': level, 'name': self.name}

        if 'timestamp' in self._template_keys:
            params['timestamp'] = self._get_timestamp()

        if {'exec_src', 'exec_line', 'exec_func', 'exec_proc'}.intersection(set(self._template_keys)):
            exec_info = self._get_exec_info()
            params.update(exec_info)

        if exception:
            params['message'] = '{}\n'.format(message) + '\n'.join(traceback.format_exc().splitlines())

        for key, value in self.additional_context.items():
            if inspect.isfunction(value):
                params[key] = value()
            else:
                params[key] = value

        for key, value in kwargs.items():
            params[key] = value

        log_line = self._formatter.format_entry(params)
        for handler in self._handlers:
            handler.write(log_line)

    def _get_timestamp(self):
        """gets a formatted timestamp

        :return: the current time in ISO 8601 string format
        :rtype: str
        """
        if self._timezone_aware:
            ts = arrow.utcnow().to(self.timezone)
        else:
            ts = datetime.now()
        ts = ts.isoformat()
        return ts

    def _get_exec_info(self):
        """gets execution information

        :return: a dictionary of execution infomation
        :rtype: dict
        """
        frame = sys._getframe(2)
        fname, line, funcname, _, __ = inspect.getframeinfo(frame)
        return {
            'exec_src': fname,
            'exec_func': funcname,
            'exec_line': line,
            'exec_proc': os.getpid(),
        }

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
        self._log(message=str(exception), level=LogLevel.EXCEPTION, exception=exception)
