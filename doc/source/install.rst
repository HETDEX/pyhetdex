Installation
************

Instructions
============

.. _sourceinst:

From local ``pyhetdex`` copy
----------------------------

First you need to obtain the source ``pyhetdex`` code with ::

  svn checkout svn://luna.mpe.mpg.de/pyhetdex

or ::

  svn checkout svn://luna.mpe.mpg.de/pyhetdex/trunk pyhetdex

if only the trunk is desired.

Once this command has finished you can install ``pyhetdex`` using `pip
<https://pip.pypa.io/en/latest/>`_ :: 

  pip install /path/to/pyhetdex

or ::

  cd /path/to/pyhetdex
  pip install .

where ``/path/to/pyhetdex`` is the base directory containing the ``setup.py``
file.

The above command installs ``pyhetdex`` in a system directory, so might be
necessary to use superuser powers, a.k.a. ``sudo``, to succeed. It is possible
to install the software in the user directories, usually
``$HOME/.local/lib/pythonX.X/site-packages`` adding the option ``--user``.

An other option is to use a `virtual environment
<https://virtualenv.pypa.io/en/latest/>`_ [#venvw]_: in this case ``pyhetdex`` will
be installed inside the environment with the above command.

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
    
  * At the moment ``pyhetdex`` is under active development, so we suggest to
    follow the instructions in :ref:`inst_devel`
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
