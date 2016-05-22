from enum import Enum


class LogLevel(Enum):
    """
    ``LogLevel`` is an enum for controlling log entries. Levels are hierarchical in that when set as the logger's
    level any logger call to a level less than that minimum will be discarded.
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
