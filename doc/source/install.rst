Installation
************

Instructions
============

.. _install:

The recommended way
-------------------

The recommended way to install pyhetdex is using `pip <https://pip.pypa.io/en/latest/>`_::

    pip install --extra-index-url https://gate.mpe.mpg.de/pypi/simple/ pyhetdex

It's possible to set the extra index URL permanently by adding the following lines
to the ``$HOME/.pip/pip.conf`` file::

    [global]
    extra-index-url = https://gate.mpe.mpg.de/pypi/simple

or exporting the environment variable::

    export PIP_EXTRA_INDEX_URL=https://gate.mpe.mpg.de/pypi/simple

The list of released versions can be seen `on the MPE pypi server
<https://gate.mpe.mpg.de/pypi/simple/pyhetdex/>`_. A specific version can be
installed using `specifiers
<https://pip.pypa.io/en/stable/reference/pip_install/#requirement-specifiers>`_,
e.g. issuing ``pip install pyhetdex==0.5``.

``pip`` will take care of installing :ref:`pyhetdex dependances <Dependances>`.

We suggest you install pyhetdex into a `virtualenv
<https://virtualenv.pypa.io/en/stable/>`_, in an `anaconda
<https://www.continuum.io/downloads>`_/`conda
<http://conda.pydata.org/docs/index.html>`_ or in similar environments.

Of course it is also possible to install pyhetdex without any of the above with::

    pip install --user --extra-index-url https://gate.mpe.mpg.de/pypi/simple/ pyhetdex

This way the pyhetdex executables are installed in ``$HOME/.local/bin``, so make
sure to add this to the environment variable ``PATH`` to be able to easily use
them on the command line. The use of ``sudo`` when installing with pip is
`discouraged
<http://stackoverflow.com/questions/21055859/what-are-the-risks-of-running-sudo-pip>`_
and potentially harmful.

.. _sourceinst:

From local ``pyhetdex`` copy
----------------------------

If you develop pyhetdex or want to use always the latest version, you can
install it directly from the checked out svn repository.
First you can obtain the source ``pyhetdex`` code with ::

  svn checkout svn://luna.mpe.mpg.de/pyhetdex/trunk pyhetdex

If you already have the repository, you can of course keep it up to date with
``svn update``

Then you can install the library with::

  pip install /path/to/pyhetdex

or ::

  cd /path/to/pyhetdex
  pip install .

where ``/path/to/pyhetdex`` is the base directory containing the ``setup.py``
file.

.. _svninst:

From online svn repository
--------------------------

It is also possible to install ``pyhetdex`` directly from the svn repository
with ::

  pip install svn+svn://luna.mpe.mpg.de/pyhetdex/trunk#egg=pyhetdex

If you want to install a specific commit or from a different branch or tag, you
can do it issuing one of the following commands ::

    pip install svn+svn://luna.mpe.mpg.de/pyhetdex/trunk@5#egg=pyhetdex
    pip install svn+svn://luna.mpe.mpg.de/pyhetdex/tag/v0.0.0#egg=pyhetdex

Other ways
----------

Once you obtained the source code as in :ref:`sourceinst`, you can install the
code also using the good old ::

    cd /path/to/pyhetdex
    python setup.py build
    python setup.py install

We do not recommend this method.

.. note::
    
  * If the installation gets interrupted with an error like::

      ImportError: No module named 'numpy'

    run ``pip install numpy`` and then retry ``pyhetdex`` installation

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
  six

.. _optdep:

Optional dependences
--------------------

* testing::

   pytest
   pytest-cov
   pytest-xdist
   pytest-catchlog
   peewee

   tox

* documentation::

    sphinx
    numpydoc
    alabaster

* automatic documentation build::

    sphinx-autobuild

.. _inst_devel:

Development
===========

If you develop ``pyhetdex`` we suggest to checkout the svn
repository and to install it in `"editable" mode
<https://pip.pypa.io/en/latest/reference/pip_install.html#editable-installs>`_
and to install all the optional dependances::

  cd /path/to/pyhetdex
  pip install -e .[livedoc]

You can also use [not recommended] ::

    python setup.py develop

See :doc:`contributions` for more information.

.. rubric:: Footnotes

.. [#venvw] Maybe with the help of `virtualenvwrapper
  <http://virtualenvwrapper.readthedocs.org/en/latest/index.html>`_
