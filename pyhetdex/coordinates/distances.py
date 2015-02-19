"""Distances on sky

This module contain functionalities to measure angular distances between
objects

.. todo::
    :func:`~angular_separation_deg`: the test fails. Where it is possible to get a
    reference value?
    http://cads.iiap.res.in/tools/angularSeparation and
    http://www.asdc.asi.it/dist.html gives very different answers, and none of
    them agrees with the output of the function
"""

import numpy as np


# -----------------------------------------------------------------------------
def angular_separation_deg(ra1, dec1, ra2, dec2):
    """Calculates the angular separation of two positions on the sky, assuming
    a tangent plane projection.

    Parameters
    ----------
    ra1: float
        R.A. in decimal degrees for position 1
    dec1: float
        dec. in decimal degrees for position 1
    ra2: float or numpy array
        R.A. in decimal degrees for position 2
    dec1: float or numpy array
        dec. in decimal degrees for position 2

    Returns
    -------
    r: float or numpy array
        angular separation in decimal degrees

    Notes
    -----
        separation has to be less than 90 deg
    """
    rad_ra1 = np.radians(ra1)
    rad_dec1 = np.radians(dec1)

    rad_ra2 = np.radians(ra2)
    rad_dec2 = np.radians(dec2)

    cosC = (np.sin(rad_dec2) * np.sin(rad_dec1))
    cosC += (np.cos(rad_dec2) * np.cos(rad_dec1) * np.cos(rad_ra2 - rad_ra1))

    x = (np.cos(rad_dec1) * np.sin(rad_ra2 - rad_ra1)) / cosC
    y = ((np.cos(rad_dec2) * np.sin(rad_dec1)) - (np.sin(rad_dec2) *
         np.cos(rad_dec1) * np.cos(rad_ra2 - rad_ra1))) / cosC

    r = np.degrees(np.sqrt(x * x + y * y))

    return r
