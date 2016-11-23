"""Distances on sky

This module contain functionalities to measure angular distances between
objects

Updated using the function from http://www.astronomycafe.net/qadir/q1890.html

http://cads.iiap.res.in/tools/angularSeparation and
http://www.asdc.asi.it/dist.html give now consistent answers for

    ra1, dec1 = 31.4324, 68.5432
    ra2, dec2 = 45.65, 23.452

and

    ra1, dec1 = 100.2, -16.58
    ra2, dec2 = 87.5, 7.38
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import warnings

import numpy as np

with warnings.catch_warnings():
    warnings.simplefilter("always")
    warnings.warn('The "{}" module has been deprecated and'
                  ' will be removed in a future release.'
                  ' Please contact the developers if you have reasons to keep'
                  ' it'.format(__name__),
                  DeprecationWarning)

# -----------------------------------------------------------------------------
def angular_separation_deg(ra1, dec1, ra2, dec2):
    """Calculates the angular separation of two positions on the sky, assuming
    a tangent plane projection.

    Parameters
    ----------
    ra1 : float
        R.A. in decimal degrees for position 1
    dec1 : float
        dec. in decimal degrees for position 1
    ra2 : float or numpy array
        R.A. in decimal degrees for position 2
    dec1 : float or numpy array
        dec. in decimal degrees for position 2

    Returns
    -------
    r : float or numpy array
        angular separation in decimal degrees

    Notes
    -----
        separation has to be less than 90 deg

    Examples
    --------

    .. testsetup::

        from pyhetdex.coordinates.distances import angular_separation_deg

    >>> ra1, dec1 = 31.4324, 68.5432
    >>> ra2, dec2 = 45.65, 23.452
    >>> print(round(angular_separation_deg(ra1, dec1, ra2, dec2), 10))
    45.9168596229
    """
    rad_ra1 = np.radians(ra1)
    rad_dec1 = np.radians(dec1)

    rad_ra2 = np.radians(ra2)
    rad_dec2 = np.radians(dec2)

    cosC = (np.sin(rad_dec2) * np.sin(rad_dec1))
    cosC += (np.cos(rad_dec2) * np.cos(rad_dec1) * np.cos(rad_ra2 - rad_ra1))

    # x = (np.cos(rad_dec1) * np.sin(rad_ra2 - rad_ra1)) / cosC
    # y = ((np.cos(rad_dec2) * np.sin(rad_dec1)) - (np.sin(rad_dec2) *
    #      np.cos(rad_dec1) * np.cos(rad_ra2 - rad_ra1))) / cosC

    # r = np.degrees(np.sqrt(x * x + y * y))

    return np.rad2deg(np.arccos(cosC))
