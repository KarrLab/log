=====
 API
=====

``log``'s main entry point for most use cases will be::

    from log import Logger

which provides sane defaults and easy logging functionality. This, however, is not the full capabilities of the
library. Under the hood there's a much more powerful API that can be accessed and customized.

------------
 log.errors
------------

.. currentmodule:: log.errors

.. autoclass:: BadTemplateError

.. autoclass:: ConfigurationError

.. autoclass:: HandlerNotFoundError

.. autoclass:: FormatterNotFoundError

------------
 log.levels
------------

.. currentmodule:: log.levels

.. autoclass:: LogLevel

----------------
 log.formatters
----------------

.. currentmodule:: log.formatters

.. autoclass:: TemplateStyle
   :members:

.. autoclass:: Formatter
   :special-members: __init__
   :members:

--------------
 log.handlers
--------------

.. currentmodule:: log.handlers

.. autoclass:: _HandlerInterface

.. autoclass:: StreamHandler
   :special-members: __init__
   :members:

.. autoclass:: log.handlers.FileHandler()
   :special-members: __init__
   :members:

.. autoclass:: log.handlers.SocketHandler()
   :special-members: __init__
   :members:

-------------
 log.loggers
-------------

.. currentmodule:: log.loggers

.. autoclass:: Logger
   :special-members: __init__
   :members:
