class BadTemplateError(Exception):
    """
    raised when some soft of conflict in reading or parsing the template occurs
    """
    pass


class ConfigurationError(Exception):
    """
    raised when initializing or updating an object could result in an unstable or unusable state
    """
    pass


class HandlerNotFoundError(Exception):
    """
    raised when trying to use a specific handler that isn't registered to the logger
    """
    pass


class FormatterNotFoundError(Exception):
    """
    raised when trying to use a specific formatter that isn't registered to the logger
    """
    pass
