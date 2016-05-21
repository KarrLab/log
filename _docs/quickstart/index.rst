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
