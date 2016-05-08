=====
 LOG
=====

.. image:: https://travis-ci.org/vforgione/log.svg?branch=master

because you deserve better than log4j


--------------
 installation
--------------

pip
---

you can install via pip::

    $ pip install log

if you want timezone support in the log entries, install the arrow extras::

    $ pip install log[arrow]

if you want to contribute, install the dev extras::

    $ pip install log[dev]

git
---

clone and run setup.py::

    $ git clone https://github.com/vforgione/log.git
    $ cd log
    $ virtualenv -p python3 .env
    $ source .env/bin/activate
    $ pip install -e .

if you want timezone support in the log entries, install the arrow extras::

    $ pip install "file://$(pwd)#egg=log[arrow]"

if you want to contribute, install the dev extras::

    $ pip install "file://$(pwd)#egg=log[dev]"


---------------
 run the tests
---------------

to run the tests you must either install the dev extras (see above). then, simply run pytest::

    $ py.test tests

to see the logs as the tests run::

    $ py.test tests -s
