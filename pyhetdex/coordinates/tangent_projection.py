"""Tangent projection transformation

.. moduleauthor:: Maximilian Fabricius <>

:meth:`~TangentPlane.raDec2xy` and :meth:`~TangentPlane.xy2raDec` implementations are
taken from sections 3.1.1 and 3.1.2 of [1]_

Examples
--------

.. testsetup:: *

    from pyhetdex.coordinates.tangent_projection import TangentPlane 

Example of use of this module::

    >>> ra0 = 0.
    >>> dec0 = 70.
    >>> rot = 0.
    >>> x_in, y_in = 10., 0.
    >>> # multiply by -1 to make positive x point east for 0 Deg rotation
    >>> tp = TangentPlane(ra0=ra0, dec0=dec0, rot=rot, x_scale= -1, y_scale=1)
    >>> ra, dec = tp.xy2raDec(x_in, y_in)
    >>> x_out, y_out = tp.raDec2xy(ra, dec)
    >>> print(round(ra, 10), round(dec, 10))
    -0.0081216788 69.999999815
    >>> print(round(x_out, 10), round(y_out, 10))
    10.0 0.0
    >>> print(abs(x_out - x_in) < 1e-10, abs(y_out - y_in) < 1e-10)
    True True
    >>> # Naive calculation
    >>> import numpy as np
    >>> print(round(-1. * (ra - ra0) * 3600. * np.cos(np.deg2rad(dec0)), 10))
    9.999999933
    >>> print(round((dec - dec0) * 3600., 10))
    -0.0006660073

.. todo::
    check the module and its the documentation

References
----------
.. [1] Eric W. Greisen, AIPS Memo 27, Non-linear Coordinate Systems in *AIPS*,
  Reissue of November 1983 version, 1993,
  ftp://ftp.aoc.nrao.edu/pub/software/aips/TEXT/PUBL/AIPSMEMO27.PS

Attributes
----------
DEGPERRAD : float
    Degrees per radians
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np


DEGPERRAD = 57.295779513082323


class TangentPlane(object):
    """Contains the necessary information to translate from on-sky RA and DEC
    coordinates on the tangent plane.

    Parameters
    ----------
    ra0, dec0 : float
        ra and dec coordinate that correspond to ``x=0`` and ``y=0`` in the
        tangent plane
    rot : float
        Rotation measured East of North such that a
        galaxy with a +10 Deg position angle on sky would be aligned with
        the y-axis in tangent plane is rotated by +10 Deg.
    x_scale, y_scale  : float, optional
        plate scale.

    Notes
    -----
        All the above parameters are saved into the corresponding attributes

        When ``x_scale=-1`` and ``y_scale=1`` the tangent plane is
        perfect in arcseconds.
    """

    def __init__(self, ra0, dec0, rot, x_scale=-1., y_scale=1.):
        self.ra0 = ra0
        self.dec0 = dec0
        self.rot = rot
        self.x_scale = x_scale
        self.y_scale = y_scale

    def raDec2xy(self, ra_in, dec_in):
        """Direct tangent transform

        Calculate x and y coordinates for positions in the IFUAstrom coordinate
        frame.

        Parameters
        ----------
        ra_in, dec_in : nd-array
            ra and dec coordinate in degrees

        Returns
        -------
        x_out, y_out : nd-arrays
            x and y coordinates (in IFUAstrom coordinates, i.e. arcsec).
        """
        ra0, dec0 = self.ra0, self.dec0
        rot = self.rot
        x_scale = self.x_scale * DEGPERRAD
        y_scale = self.y_scale * DEGPERRAD

        rra0 = np.deg2rad(ra0)
        rdec0 = np.deg2rad(dec0)
        rrot = np.deg2rad(rot)

        rra_in = np.deg2rad(ra_in)
        rdec_in = np.deg2rad(dec_in)

        # AIPS Memo 27, 3.1.1
        xhat = np.cos(rdec_in) * np.sin(rra_in - rra0)
        xhat /= (np.sin(rdec_in) * np.sin(rdec0) +
                 np.cos(rdec_in) * np.cos(rdec0) * np.cos(rra_in - rra0))
        yhat = np.sin(rdec_in) * np.cos(rdec0)
        yhat -= np.cos(rdec_in) * np.sin(rdec0) * np.cos(rra_in - rra0)
        yhat /= (np.sin(rdec_in) * np.sin(rdec0) +
                 np.cos(rdec_in) * np.cos(rdec0) * np.cos(rra_in - rra0))

        # rotation and scaling
        x = xhat * np.cos(rrot) * x_scale + yhat * np.sin(rrot) * y_scale
        y = -xhat * np.sin(rrot) * x_scale + yhat * np.cos(rrot) * y_scale

        return x * 3600., y * 3600.

    def xy2raDec(self, x_in, y_in):
        """inverse tangent transform

        Calculates RA and DEC coordinates for positions in the IFUAstrom
        coordinate frame.

        Parameters
        ----------
        x_in, y_in : nd-array
            x and y coordinate in arcseconds

        Returns
        -------
        ra_out, dec_out : nd-arrays
            RA/DEC coordinates in degree
        """
        ra0, dec0 = self.ra0, self.dec0
        rot = self.rot
        x_scale = self.x_scale * DEGPERRAD
        y_scale = self.y_scale * DEGPERRAD

        rra0 = np.deg2rad(ra0)
        rdec0 = np.deg2rad(dec0)
        rrot = np.deg2rad(rot)

        # rotation and scaling
        xhat = (x_in/3600.) * np.cos(rrot)/x_scale
        xhat -= (y_in/3600.) * np.sin(rrot)/y_scale
        yhat = (x_in/3600.) * np.sin(rrot)/x_scale
        yhat += (y_in/3600.) * np.cos(rrot)/y_scale

        # AIPS Memo 27, 3.1.2
        rra_out = rra0 + np.arctan(xhat/(np.cos(rdec0) - yhat * np.sin(rdec0)))
        rdec_out = np.arctan(np.cos(rra_out - rra0) * (yhat * np.cos(rdec0) +
                                                       np.sin(rdec0)) /
                             (np.cos(rdec0) - yhat * np.sin(rdec0)))

        return np.rad2deg(rra_out), np.rad2deg(rdec_out)
