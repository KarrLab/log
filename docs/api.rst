=====
 API
=====

``log``'s main entry point for most use cases will be::

    from log import Logger

which provides sane defaults and easy logging functionality. This, however, is not the full capabilities of the
library. Under the hood there's a much more powerful API that can be accessed and customized.

--------
 errors
--------

.. autoclass:: log.errors.ConfigurationError

--------
 levels
--------

.. autoclass:: log.levels.LogLevel


------------
 formatters
------------

.. autoclass:: log.formatters.TemplateStyle

.. autoclass:: log.formatters.Formatter()
   :special-members: __init__
   :members:

----------
 handlers
----------

.. autoclass:: log.handlers.StreamHandler()
   :special-members: __init__
   :members:

.. autoclass:: log.handlers.FileHandler()
   :special-members: __init__
   :members:

.. autoclass:: log.handlers.SocketHandler()
   :special-members: __init__
   :members:

---------
 loggers
---------

.. autoclass:: log.loggers.Logger()
   :special-members: __init__
   :members:
   :undoc-members:
