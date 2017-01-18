"""World coordinate system
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import warnings

with warnings.catch_warnings():
    warnings.simplefilter("always")
    warnings.warn('The "{}" module has been deprecated and'
                  ' will be removed in a future release.'
                  ' Please contact the developers if you have reasons to keep'
                  ' it'.format(__name__),
                  DeprecationWarning)


def deg2pix(degree, scale=1.698):
    """Convert degrees in pixels, given a pixel scale

    Parameters
    ----------
    degree : float
        angle to convert
    scale : float, optional
        pixel scale

    Returns
    -------
    float
        number of pixels
    """
    return degree * 3600. / scale
