"""Tangent plane projection transformation.


.. warning::
    This module is temporary.
    The chosen implementation of the tangent plane projection will go into
    :mod:`pyhetdex.coordinates.tangent_projection` and this module will be
    removed

"""
import warnings

from .tangent_projection import TangentPlane

with warnings.catch_warnings():
    warnings.simplefilter("always")
    warnings.warn('The "{}" module has been deprecated and'
                  ' will be removed in a future release. Use'
                  ' "pyhetdex.coordinates.tangent_projection"'
                  ' instead'.format(__name__),
                  DeprecationWarning)
