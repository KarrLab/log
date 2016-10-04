============
 Quickstart
============

Creating loggers with ``log`` should intuitive. The loggers have a simple, predictable API that you can use in either
a sane default configuration or extend as you see fir.

------------------
 A Simple Example
------------------

The following is a really simple example of using the default logger::

    #!/usr/bin/env python

    from datetime import datetime, timedelta

    import log
    from log.levels import LogLevel

    from .whatever import func1, func2, func3, func_maybe_err


    logger = log.Logger(level=LogLevel.DEBUG)


    script_start = datetime.now()
    logger.debug('starting script at {}'.format(script_start))

    results1 = func1()
    logger.info('results of func1: {}'.format(results1))

    results2 = func2()
    logger.info('results of func2: {}'.format(results2))


    results3 = func3()
    logger.info('results of func3: {}'.format(results3))

    results4, error_message = func_maybe_err()
    if error_message:
        logger.error(error_message)
    else:
        logger.info('results of func_maybe_err: {}'.format(results4))

    try:
        1 / 0
    except ZeroDivisionError as e:
        logger.exception(e)

    script_end = datetime.now()
    logger.debug('stopping script at {}'.format(script_end))

    if script_end - script_start > timedelta(seconds=1):
        logger.warning('this took longer than expected')

If executed, you might expect something like the following::

    [2016-05-21T14:09:27.081386] [DEBUG] : starting script at 2016-05-21 14:09:27.081356
    [2016-05-21T14:09:27.081449] [INFO] : results of func1: {'status': 'normal', 'messages': None}
    [2016-05-21T14:09:30.086464] [INFO] : results of func2: 100.897
    [2016-05-21T14:09:30.086637] [INFO] : results of func3: nothing special happening here
    [2016-05-21T14:09:30.086686] [ERROR] : something went down somewhere at sometime under some circumstances
    [2016-05-21T14:09:30.086728] [EXCEPTION] : division by zero
    Traceback (most recent call last):
      File "simple.py", line 34, in <module>
        1 / 0
    ZeroDivisionError: division by zero
    [2016-05-21T14:09:30.087177] [DEBUG] : stopping script at 2016-05-21 14:09:30.087151
    [2016-05-21T14:09:30.087230] [WARNING] : this took longer than expected

-----------------------------
 On Demand Context Injection
-----------------------------

In some cases, you might want to inject additional context into your logs on a per-call basis. This can be achieved by
either supplying context values via kwargs when you call logger methods or through setting up additional context when
creating the logger.

Per-Call
--------

Supplying context per-call::

    #!/usr/bin/env python

    import log
    import requests


    template = '[{timestamp}] [{level}] [{name}] : [status_code={res.status_code}] [headers={res.headers}] {message}'

    logger = log.Logger(name='sites', template=template, timezone_aware=True, timezone='America/Chicago')

    res = requests.get('https://google.com/')
    logger.info('google.com', res=res)

    res = requests.get('https://github.com/')
    logger.info('github.com', res=res)

    res = requests.get('https://github.com/log4j-works-for-python')
    logger.info('github.com/log4j-works-for-python', res=res)

Which would look something like this::

    [2016-05-21T14:44:31.408652-05:00] [INFO] [sites] : [status_code=200] [headers={'Content-Encoding': 'gzip', 'Content-Type': 'text/html; charset=ISO-8859-1'}] google.com
    [2016-05-21T14:44:32.006688-05:00] [INFO] [sites] : [status_code=200] [headers={'Content-Encoding': 'gzip', 'Content-Type': 'text/html; charset=UTF-8'}] github.com
    [2016-05-21T14:44:32.220063-05:00] [INFO] [sites] : [status_code=404] [headers={'Content-Encoding': 'gzip', 'Content-Type': 'text/html; charset=UTF-8'}] github.com/log4j-works-for-python

Using `additional_context`
--------------------------

Using the `additional_context` params when creating the logger::

    #!/usr/bin/env python

    import uuid

    import log
    from log.levels import LogLevel


    def get_uuid():
        return str(uuid.uuid4())


    template = '[{uuid}] [{level}] : {message}'

    logger = log.Logger(template=template, level=LogLevel.DEBUG, additional_context={'uuid': get_uuid})

    logger.debug('debug')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')

Which would look like::

    [3524d5f2-8d66-4b7a-9f27-8415c1cbe208] [DEBUG] : debug
    [cf06d83c-2487-435c-a452-ade44642041a] [INFO] : info
    [191304e8-20fc-42f6-bad2-39f84b7a5d00] [WARNING] : warning
    [2eeb0c8a-6d98-4b83-8b53-3aff1a7b4fe9] [ERROR] : error

Note that adding context during execution will override anything you set for that call::

    #!/usr/bin/env python

    import uuid

    import log
    from log.levels import LogLevel


    def get_uuid():
        return str(uuid.uuid4())


    template = '[{uuid}] [{level}] : {message}'

    logger = log.Logger(template=template, level=LogLevel.DEBUG, additional_context={'uuid': get_uuid})

    logger.debug('debug')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')

    logger.info('this was added when `info` was called', uuid='yay special cases')
    logger.info('back to normal')

Which would produce::

    [f07a094a-53ea-4f8a-8ed4-53ec1a4e8aee] [DEBUG] : debug
    [6d1044cd-0f6e-49f8-bb40-92355b843365] [INFO] : info
    [6c4e5717-e3b5-43f4-87f9-ce56718db4de] [WARNING] : warning
    [e3603948-8058-4e26-81d3-1878c893f53f] [ERROR] : error
    [yay special cases] [INFO] : this was added when `info` was called
    [6a791cdc-1033-4d07-aaa0-0a4919121a27] [INFO] : back to normal


--------------------
 Context Management
--------------------

``log`` employs simple context management for `Logger`s. If you have several formatters or handlers or both setup and
find yourself needing to switch between them in given situations, doing so is trivial using a `with` block::

    #!/usr/bin/env python

    import sys

    from log import Logger
    from log.formatters import Formatter
    from log.handlers import StreamHandler


    logger = Logger()  # default formatter and stdout handler
    err_formatter = Formatter(template='OH CRAP: {message}', name='err')
    logger.add_formatter(err_formatter)
    err_handler = StreamHandler(stream=sys.stderr, name='err')
    logger.add_handler(err_handler)

    logger.info('info!!!')  # uses default formatter and writes to stdout and stderr

    with logger.using(err_formatter) as err_logger:
        err_logger.warning('watch out')  # uses the 'err' formatter and writes to stdout and stderr

    with logger.only(err_handler) as err_logger:
        err_logger.warning('watch out again!')  # writes to only stderr using the default formatter

    with logger.using('err').only('err') as err_logger:  # you can use their names instead
        err_logger.error('air or')  # uses the 'oh crap' format and only writes it to stderr
