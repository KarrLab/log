import syslog
from enum import Enum


class LogLevel(Enum):
    """
    log verbosity control
    """

    DEBUG = 0       # logs verbose information
    INFO = 1        # logs general information
    WARNING = 2     # logs warning information
    ERROR = 3       # logs error information
    EXCEPTION = 4   # logs exception stack traces

    def __str__(self):
        return self.name.upper()

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __eq__(self, other):
        return self.value == other.value

    def __le__(self, other):
        return self.value <= other.value

    def __lt__(self, other):
        return self.value < other.value

    @classmethod
    def get_level_for_log_method(cls, method):
        if method == 'debug':
            return cls.DEBUG
        elif method == 'info':
            return cls.INFO
        elif method == 'warning':
            return cls.WARNING
        elif method == 'error':
            return cls.ERROR
        elif method == 'exception':
            return cls.EXCEPTION
        else:
            raise ValueError('Could not translate log method named `{method}`'.format(method=method))

    @property
    def syslog_eq(self):
        """ gets the equivalent syslog level """
        if self.value == 0:
            return syslog.LOG_DEBUG
        elif self.value == 1:
            return syslog.LOG_INFO
        elif self.value == 2:
            return syslog.LOG_WARNING
        else:
            return syslog.LOG_ERR
