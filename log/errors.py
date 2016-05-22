class ConfigurationError(Exception):  # pragma: no cover
    """
    ``ConfigurationError`` is a simple pass through to ``Exception``. It is raised by ``Logger`` when a given
    configuration cannot produce a well configured logger instance.
    """
    pass
