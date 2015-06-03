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

*Every part of the code should be tested.*

To every unit of code, should correspond one or more tests.

To run the tests execute::

  python setup.py nosetests

The command also takes care to install the test dependences if they are not
already available on the system.

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
