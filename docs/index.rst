=====
 log
=====

`because you deserve better than log4j`

----------
 Contents
----------

.. toctree::
   :maxdepth: 2

   installation
   quickstart
   api
   testing

----------
 Overview
----------

**What is log?**

``log`` is designed to be a more pythonic logger than the current logging module in the standard library. The focus of
``log`` is to provide a consistent and simple API for logging information from applications and scripts that can be
easily extended to suit whatever the developer's needs are. It uses common pythonic patterns and sane defaults so
that you can easily configure a logger and get on with your life.

**What's wrong with logging?**

The built in logging module that ships with Python is trash. The logging module was built to emulate as closely the
Java logging module `log4j`. The API is unnecessarily complicated and contains numerous anti-patterns when working with
Python. It is extremely brittle when extended and becomes a major stumbling block in the development process.

Take for example adding additional context to log entries: you can create and use an adapter, use a custom filter,
hack the formatter or inject data through a dual layer keyword processor from the logger. That's 4 separate ways of
achieving the same outcome. However, each of these ways has its own major flaw. Adapters do not implement the same
API as loggers and therefor break when used as logger replacements. Filters can lose context easily in threads (which
by now you probably should just use ``asyncio`` instead of threading). Using the logger to supply data becomes tedious
and forces you to wrap its API. Hacking around the formatter could have unintended side effects and inconsistent log
entry formats, thus making it that much more difficult to parse later.

Overall, working with the built in logging module is a painful experience that hopefully ``log`` with alleviate.

**Why this and not something else?**

There are lots of other solid logging libraries available for Python. However, most of them are built on top of the
built in logging library and are intended for special use cases. As stated, the goal of this library is to provide
a simple and consistent logger for whatever you're building that does its job and gets out of your way.
