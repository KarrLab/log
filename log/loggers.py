import inspect
import os
import sys
import traceback
from datetime import datetime

from .errors import ConfigurationError, FormatterNotFoundError
from .formatters import Formatter
from .handlers import _HandlerInterface, StreamHandler
from .levels import LogLevel

try:
    import arrow
    _arrow_available = True
except ImportError:           # pragma: no cover
    _arrow_available = False  # pragma: no cover


class Logger(object):
    """
    ``Logger`` writes log entries.

    >>> logger = Logger(timezone='America/Chicago')
    >>> logger.info('really simple logging')
    [2016-05-21T14:44:31.408652-05:00] [INFO] : really simple logging
    """

    DEFAULT_TEMPLATE = '[{timestamp}] [{level}] : {message}'
    BASE_LOG_PARAMS = ['timestamp', 'level', 'name', 'message', 'src', 'line', 'func', 'proc']

    def __init__(self, name=None, level=None, template=None, formatters=None, handlers=None, timezone=None,
                 additional_context=None):
        """
        :param name: the name of the logger
        :type name: str
        :param level: the minimum logging level
        :type level: LogLevel
        :param template: the template to format the log entries
        :type template: str
        :param formatters: a list of formatters to use for formatting message
        :type formatters: Formatter
        :param handlers: a list of handlers to write the messages
        :type handlers: _HandlerInterface
        :param timezone: the name of the timezone to convert the timestamp to
        :type timezone: str
        :param additional_context: values to inject for additional formatting context
        :type additional_context: dict
        """
        self.name = name or __name__
        self.level = level or LogLevel.INFO
        self.additional_context = additional_context or dict()

        self._handlers = set()
        self._formatters = set()
        self._default_formatter = None
        self._template = None
        self._timezone = None

        handlers = handlers or [StreamHandler(stream=sys.stdout)]
        for handler in handlers:
            self.add_handler(handler)

        formatters = formatters or [Formatter(template=self.DEFAULT_TEMPLATE)]
        for formatter in formatters:
            self.add_formatter(formatter)

        tmp = list(filter(lambda f: f.name == 'default', self._formatters))
        if not tmp:
            raise ValueError("No default formatter(s) provided for log '{}'.".format( name ) )
        self._default_formatter = tmp[0]

        if template:
            self._apply_template_to_formatters(template)
            self._template = template
        else:
            self._template = self.DEFAULT_TEMPLATE

        if timezone:
            self._set_timezone(timezone)
        else:
            self._timezone = None

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        return self

    @property
    def handlers(self):
        return self._handlers

    @property
    def formatters(self):
        return self._formatters

    @property
    def default_formatter(self):
        return self._default_formatter

    @default_formatter.setter
    def default_formatter(self, formatter):
        old_default = self._default_formatter
        self._formatters.remove(old_default)
        formatter.name = 'default'
        self.add_formatter(formatter)
        self.add_formatter(old_default)

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, template):
        self._apply_template_to_formatters(template)
        self._template = template

    @property
    def timezone(self):
        return self._timezone

    @timezone.setter
    def timezone(self, timezone):
        self._set_timezone(timezone)

    def debug(self, message, **kwargs):
        """writes a debug log entry

        :param message: the message of the log entry
        :param message: str

        :param kwargs: arbitrary key/value pairs to be used as additional interpolation context;
            if the call to debug() is wrapped in other functions, set 'local_call_depth' to application 
            call depth prior to calling debug() to obtain proper log call location
        :type kwargs: dict
        """
        if self.level <= LogLevel.DEBUG:
            self._log(message, LogLevel.DEBUG, **kwargs)

    def info(self, message, **kwargs):
        """writes an informational log entry

        :param message: the message of the log entry
        :param message: str

        :param kwargs: arbitrary key/value pairs to be used as additional interpolation context
            if the call to info() is wrapped in other functions, set 'local_call_depth' to application 
            call depth prior to calling info() to obtain proper log call location
        :type kwargs: dict
        """
        if self.level <= LogLevel.INFO:
            self._log(message, LogLevel.INFO, **kwargs)

    def warning(self, message, **kwargs):
        """writes a warning log entry

        :param message: the message of the log entry
        :param message: str

        :param kwargs: arbitrary key/value pairs to be used as additional interpolation context
            if the call to warning() is wrapped in other functions, set 'local_call_depth' to application 
            call depth prior to calling warning() to obtain proper log call location
        :type kwargs: dict
        """
        if self.level <= LogLevel.WARNING:
            self._log(message, LogLevel.WARNING, **kwargs)

    def error(self, message, **kwargs):
        """writes an error log entry

        :param message: the message of the log entry
        :param message: str

        :param kwargs: arbitrary key/value pairs to be used as additional interpolation context
            if the call to error() is wrapped in other functions, set 'local_call_depth' to application 
            call depth prior to calling error() to obtain proper log call location
        :type kwargs: dict
        """
        self._log(message, LogLevel.ERROR, **kwargs)

    def exception(self, exception):
        """writes an exception and traceback log entry

        :param exception: the caught exception
        :param exception: Exception
        """
        self._log(message=str(exception), level=LogLevel.EXCEPTION, exception=exception)

    def add_handler(self, handler):
        """adds a handler to the logger

        :param handler: the handler to be added
        :type handler: _HandlerInterface
        """
        self._name_handler(handler)
        self._handlers |= {handler}

    def remove_handler(self, handler):
        """removes a handler from the logger

        :param handler: the handler to be removed
        :type handler: _HandlerInterface
        """
        self._handlers.remove(handler)
        remaining_handlers = [h for h in self._handlers]
        self._handlers.clear()
        for handler in remaining_handlers:
            handler.name = None
            self.add_handler(handler)

    def add_formatter(self, formatter):
        """adds a formatter to the logger

        :param formatter: the formatter to be added
        :type formatter: Formatter
        """
        self._name_formatter(formatter)
        self._formatters |= {formatter}

    def remove_formatter(self, formatter):
        """removes a formatter from the logger

        :param formatter: the formatter to be removed
        :type formatter: Formatter
        """
        reassign_to_first = formatter.name == 'default'
        self._formatters.remove(formatter)
        if len(self._formatters) == 1 or reassign_to_first:
            last_formatter = self._formatters.pop()
            last_formatter.name = 'default'
            self._formatters |= {last_formatter}
            self._default_formatter = last_formatter

    def clone(self):
        """creates a copy of the logger instance

        :returns: a copy of the current logger
        """
        logger = Logger()
        logger.name = self.name
        logger.level = self.level
        logger.additional_context = self.additional_context
        logger._handlers = self._handlers
        logger._formatters = self._formatters
        logger._default_formatter = self._default_formatter
        logger._template = self._template
        logger._timezone = self._timezone
        return logger

    def using(self, formatter):
        """specifies a particular formatter to be used when you want a non-default

        :param formatter: the name or instance of a logger's formatter
        :type formatter: str or Formatter

        :returns: a clone of the logger with the selected formatter set as the only formatter

        :raises: FormatterNotFoundError

        >>> logger = Logger()
        >>> formatter = Formatter(template='SOMETHING WENT TERRIBLY WRONG: {message}', name='terribly_wrong')
        >>> logger.add_formatter(formatter)
        >>> try:
        ...     something_really_dangerous()
        ... except Exception as e:
        ...     logger.info('oh shit!')
        ...     with logger.using('terribly_wrong') as lgr:
        ...         lgr.exception(e)
        ...
        [2016-05-28T14:23:32.089234] [INFO] : oh shit!
        SOMETHING WENT TERRIBLY WRONG: error description and traceback
        """
        if isinstance(formatter, Formatter):
            formatter_name = formatter.name
        else:
            formatter_name = formatter
        try:
            existing_formatter = list(filter(lambda f: f.name == formatter_name, self._formatters))[0]
            # if it isn't the default formatter here, we don't want to override it with side effects from the clone
            new_formatter = Formatter(
                name='default', template=existing_formatter.template,
                append_new_line=existing_formatter.append_new_line)
        except IndexError:
            raise FormatterNotFoundError("Couldn't find formatter {}".format(formatter_name))
        clone = self.clone()
        clone._formatters = {new_formatter}
        clone._default_formatter = new_formatter
        return clone

    def only(self, *handlers):
        """specifies particular handlers to write the message

        :param handlers: one or more handlers to write the message
        :type handlers: str or _HandlerInterface

        :return: a clone of the logger with the selected handlers set as the only handlers

        >>> logger = Logger()  # defaults to one handler with sys.stdour
        >>> stderr = StreamHandler(sys.stderr, name='stderr')
        >>> err_log = FileHandler('/var/log/err.log', name='err_log')
        >>> logger.add_handler(stderr)
        >>> logger.add_handler(err_log)
        >>> with logger.only('stderr', 'err_log') as lgr:
        ...     lgr.error('blerg. something screwed up')  # only writes to log and stderr, not stdout
        """
        handler_names = []
        for handler in handlers:
            if isinstance(handler, _HandlerInterface):
                handler_names.append(handler.name)
            else:
                handler_names.append(handler)
        handlers = set(filter(lambda h: h.name in handler_names, self._handlers))
        clone = self.clone()
        clone._handlers = handlers
        return clone

    def _log(self, message, level, exception=None, formatter=None, handlers=None, **context):
        params = {'message': message, 'level': level, 'name': self.name}

        if formatter is None:
            formatter = self._default_formatter
        template_keys = formatter.extract_template_keys()

        if 'timestamp' in template_keys:
            params['timestamp'] = self._get_timestamp()

        if {'src', 'line', 'func', 'proc'}.intersection(set(template_keys)):
            if 'local_call_depth' in context:
                exec_info = self._get_execution_info( additional_call_depth=context['local_call_depth'] )
            else:
                exec_info = self._get_execution_info()
            params.update(exec_info)

        if exception:
            params['message'] = '{}\n'.format(message) + '\n'.join(traceback.format_exc().splitlines())

        for key, value in self.additional_context.items():
            if inspect.isfunction(value):
                params[key] = value()
            else:
                params[key] = value

        for key, value in context.items():
            params[key] = value

        log_line = formatter.format(**params)
        if handlers is None:
            handlers = self._handlers
        for handler in handlers:
            handler.write(log_line)

    def _get_timestamp(self):
        if self._timezone:
            ts = arrow.utcnow().to(self._timezone)
        else:
            ts = datetime.now()
        ts = ts.isoformat()
        return ts

    def _get_execution_info(self,additional_call_depth=0):
        frame = sys._getframe(3+additional_call_depth)
        fname, line, funcname, _, __ = inspect.getframeinfo(frame)
        return {
            'src': fname,
            'func': funcname,
            'line': line,
            'proc': os.getpid(),
        }

    def _name_handler(self, handler):
        if handler.name:
            return handler.name
        type_of_handler = type(handler)
        like_handlers = list(filter(lambda h: isinstance(h, type_of_handler), self._handlers))
        num_like_handlers = len(like_handlers)
        name = '{}{}'.format(type_of_handler.__name__, num_like_handlers)
        handler.name = name
        return name

    def _name_formatter(self, formatter):
        if formatter.name:
            return formatter.name
        num_formatters = len(self._formatters)
        if num_formatters == 0:
            name = 'default'
        else:
            name = 'Formatter{}'.format(num_formatters)
        formatter.name = name
        return name

    def _apply_template_to_formatters(self, template):
        for formatter in self._formatters:
            formatter.template = template

    def _set_timezone(self, timezone):
        if _arrow_available:
            self._timezone = timezone
        else:
            raise ConfigurationError(
                "You must install the 'timezone' extra target to use timezone aware time stamps")
