Contribute to pyhetdex
**********************

Coding style
============

All the code should be compliant with the :pep:`8`.

The code should also be thoroughly documented. We follow the `numpy style
<https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt>`_. See
the existing documentation.

Testing
=======

*Every part of the code should be tested and should run at least under python
2.7 and 3.4.*

The tests are written using the `pytest
<http://pytest.org/latest/contents.html#>`_ framework.

The preferred way to run the tests is using `tox
<https://testrun.org/tox/latest/index.html>`_, an automatised test help
package. If you have installed tox, with e.g. ``pip install tox``, you can run
it typing::

    tox

It will take care of creating virtual environments for every supported version
of python, if it exists on the system, install ``pyhetdex``, its dependences and the
packages necessary to run the tests and runs ``py.test``

We also provide a ``setuptools`` command to run ``tox``. If you run::

    python setup.py tox

all the needed dependences, among others ``tox`` itself, will be fetched
and installed in a ``.eggs`` directory. Then it will run ``tox``. This command
might fail when running in a virtual environment. If you get ``ImportError:
No module named 'numpy'`` while installing ``scipy``, install numpy by hand
``pip install [--user] numpy`` and rerun it again.

You can run the tests for a specific python version using::

    py.test

or::

    python setup.py test

You can run specific tests providing the file name(s) and, optionally the name
of a test. E.g.::

    py.test tests/test_logging_helper.py  # runs only the tests in the logging helper file
    py.test tests/test_logging_helper.py::test_log_setup  # runs only one test 

Relevant command line options::

    -v                    verbose output: print the names and parameters of the
                          tests
    -s                    capture standard output: can cause weird interactions
                          with the logging module

Some test are place holders for missing tests, non reviewed or buggy code. They
are marked as ``todo`` and they fail. It is possible to skip them invoking::

    py.test -m "not todo"

or::

    tox -- "-m 'not todo'"

A code coverage report is also created thanks to the `pytest-cov
<https://pypi.python.org/pypi/pytest-cov>`_ plugin and can be visualized opening
into a browser ``cover/index.html``. If you want a recap of the coverage
directly in the terminal you can provide one of the following options when
running ``py.test``::

    --cov-report term
    --cov-report term-missing
    
Besides running the tests, the ``tox`` command also build the documentation and
collate the coverage tests from the various python interpreters. Upon request
the documentation and the coverage html report can be deployed to a target
directory. To do it create, if necessary, the configuration file
``~/.config/tox_deploy.cfg`` and add to it a section called ``pyhetdex`` and
either one or both of the following options:

.. code-block:: ini

    [pyhetdex]
    # if given the deploys the documentation to the given dir
    doc = /path/to/dir
    # if given the deploys the coverage report to the given dir
    cover = /path/to/other/dir

    # it's also possible to insert the project name and the type of the document
    # to deploy using the {project} and {type_} placeholders. E.g
    # cover = /path/to/dir/{project}_{type_}
    # will be expanded to /path/to/dir/pyhetdex_cover


For other command line arguments type::

    py.test -h

For a list of available fixtures type::

    py.test --fixtures tests/

To every unit of code, should correspond one or more tests.

Documentation
=============

To build the documentation you need the additional dependences described in
:ref:`optdep`. They can be installed by hand or during ``pyhetdex`` installation
executing one of the following commands on a local copy::

  pip install /path/to/pyhetdex[doc]
  pip install /path/to/pyhetdex[livedoc]

The first install ``sphinx``, the ``alabaster`` theme and the ``numpydoc``
extension; the second also ``sphinx-autobuild``.

To build the documentation in html format go to the ``doc`` directory and run::

  make html

The output is saved in ``doc/build/html``. For the full list of available
targets type ``make help``.

If you are updating the documentation and want avoid the
``edit-compile-browser refresh`` cycle, and you have installed
``sphinx-autobuild``, type::

  make livehtml

then visit http://127.0.0.1:8000. The html documentation is automatically
rebuilt after every change of the source and the browser reloaded.
