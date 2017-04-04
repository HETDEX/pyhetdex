.. :py:currentmodule:: pyhetdex.tools

:py:mod:`tools.configuration` -- Configuration parser
*****************************************************

.. automodule:: pyhetdex.tools.configuration

The configuration parser
========================

.. autoclass:: pyhetdex.tools.configuration.ConfigParser
   :member-order: bysource
   :members: get_list, get_list_of_list, read_dict, _interpolate
   :undoc-members:
   :show-inheritance:


Reimplement the interpolation
=============================

The implementation of the interpolation objects has been copied from the `python
3.5 development branch <https://hg.python.org/cpython/rev/d78727872e05>`_ and
adapted to work on python 2.7.

.. autoclass:: pyhetdex.tools.configuration.Interpolation

.. autoclass:: pyhetdex.tools.configuration.BasicInterpolation
   :show-inheritance:

.. autoclass:: pyhetdex.tools.configuration.ExtendedInterpolation
   :show-inheritance:


Utilities
=========

.. autofunction:: pyhetdex.tools.configuration.override_conf
