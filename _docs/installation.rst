==============
 Installation
==============

You can install ``log`` via pip or download and build it from source.

-----
 pip
-----

To install ``log`` via pip::

   $ pip install log

There are other additional, optional installation targets as well. To use ``log`` with timezone support::

   $ pip install log[timezone]

If you want the full development requirements, install ``log`` with::

   $ pip install log[dev]

--------------------
 Download and Build
--------------------

You can also install ``log`` by downloading the source from GitHub and manually run the setup::

   $ git clone https://github.com/vforgione/log.git
   $ cd log
   $ make build

Similar to above, after building the project you can install it's optional targets with::

   $ make build-dev
