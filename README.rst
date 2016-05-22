=====
 log
=====

`because you deserve better than log4j`

.. image:: https://coveralls.io/repos/github/vforgione/log/badge.svg?branch=master
   :target: https://coveralls.io/github/vforgione/log?branch=master

.. image:: https://travis-ci.org/vforgione/log.svg?branch=master
   :target: https://travis-ci.org/vforgione/log

.. image:: https://img.shields.io/pypi/v/log.svg?style=flat
   :target: https://pypi.python.org/pypi/log

.. image:: https://readthedocs.org/projects/log/badge/?version=latest
   :target: http://log.readthedocs.io/en/latest/?badge=latest

--------------
 installation
--------------

pip
---

you can install via pip::

    $ pip install log

if you want timezone support in the log entries, install the arrow extras::

    $ pip install log[timezone]

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

    $ pip install "file://$(pwd)#egg=log[timezone]"

if you want to contribute, install the dev extras::

    $ pip install "file://$(pwd)#egg=log[dev]"


---------------
 run the tests
---------------

to run the tests you must either install the dev extras (see above). then, simply run pytest::

    $ py.test --cov log --cov-report term-missing tests 
