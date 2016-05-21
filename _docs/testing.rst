==========================
 Testing and Contributing
==========================

If you are developing ``log``, you will need to install its dev target::

   $ make build-dev


--------------------------
 Testing via the Makefile
--------------------------

The Makefile straps together `flake8` and `pytest`, as well as configuring `pytest`'s options. All you need to do is::

   $ make test

and it will build the environment and run the tests.

----------------------------
 Manually Running the Tests
----------------------------

You can also run the tests yourself. This is useful when you want to only run specific tests. The full list of
commands is listed below, but feel free to run them as needed::

   $ flake8
   $ py.test --cov log --cov-report term-missing tests

--------------
 Contributing
--------------

If you would like to contribute to ``log``, please follow these guidelines:

   - Create and develop within a feature branch.
   - Thoroughly test the code. The project currently has 100% test coverage and I'd like to keep it that way :)
   - Create or update any documentation as necessary.
   - When ready to push and open a pull request, use the Makefile process `push-feature`.

A really contrived workflow would be like this::

   $ git checkout -b my-awesome-feature
   $ vim log/loggers.py
   $ vim tests/test_loggers.py
   $ make test
   $ vim _docs/api/loggers.rst
   $ git add .
   $ git commit
   $ make push-feature
