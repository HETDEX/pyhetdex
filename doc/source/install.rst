Installation
************

Instructions
============

.. _svninst:

From online svn repository
--------------------------

The easiest way to install ``pyhetdex`` is using `pip
<https://pip.pypa.io/en/latest/>`_::

  pip install svn+svn://luna.mpe.mpg.de/pyhetdex/trunk#egg=pyhetdex

This will take care of installing :ref:`pyhetdex dependances <Dependances>`.

From local ``pyhetdex`` copy
----------------------------

If you want a local copy of ``pyhetdex``, you can checkout the repository with::

  svn checkout svn://luna.mpe.mpg.de/pyhetdex

or::

  svn checkout svn://luna.mpe.mpg.de/pyhetdex/trunk pyhetdex

if only the trunk is desired. Similarly to the :ref:`previous instructions
<svninst>` now you can install with::

  pip install /path/to/pyhetdex

or::

  cd /path/to/pyhetdex
  pip install .


.. _Dependances:

Dependances
===========

Mandatory dependences
---------------------

::

  numpy
  scipy
  astropy>=1
  Pillow
  matplotlib


.. _optdep:

Optional dependences
--------------------

* testing::

   nose>=1
   coverage
   tissue

* documentation::

    sphinx
    numpydoc
    alabaster

* automatic documentation build::

    sphinx-autobuild


Development
===========

If you develop ``pyhetdex`` we suggest to checkout the svn
repository and to install it in `"editable" mode
<https://pip.pypa.io/en/latest/reference/pip_install.html#editable-installs>`_
and to install all the optional dependances::

  cd /path/to/pyhetdex
  pip install -e .

See :doc:`contributions` for more information.

Notes and problems
==================

* We suggest to use a `virtual environment
  <https://virtualenv.pypa.io/en/latest/>`_ [#venvw]_. Outside a virtual
  environment the above command installs in a system directory, so might be
  necessary to use superuser powers, a.k.a. ``sudo``. It is possible to install
  the software in the user directory, usually ``$HOME/.local`` adding the option
  ``--user``.
* It is possible to change the version to install from svn selecting a specific
  commit::

    pip install svn+svn://luna.mpe.mpg.de/pyhetdex/trunk@5#egg=pyhetdex

  or a different branch/tag::

    pip install svn+svn://luna.mpe.mpg.de/pyhetdex/tag/v0.0.0#egg=pyhetdex

* If the installation gets interrupted with an error like::

    ImportError: No module named 'numpy'

  run ``pip install numpy`` and then retry ``pyhetdex`` installation

.. rubric:: Footnotes

.. [#venvw] Maybe with the help of `virtualenvwrapper
  <http://virtualenvwrapper.readthedocs.org/en/latest/index.html>`_
