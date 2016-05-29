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

**Why this and not something else?**

There are lots of other solid logging libraries available for Python. However, most of them are built on top of the
built in logging library and are intended for special use cases. As stated, the goal of this library is to provide
a simple and consistent logger for whatever you're building that does its job and gets out of your way.
