# Misc python library to support HETDEX software and data analysis
# Copyright (C) 2014, 2015, 2016, 2017  "The HETDEX collaboration"
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""Tangent projection transformation: a wrapper around :class:`astropy.wcs.WCS`

.. moduleauthor:: Daniel Farrow <dfarrow@mpe.mpg.de>

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
    >>> ra -= 360
    >>> print((ra).round(8), dec.round(8))
    -0.00812168 69.99999981
    >>> print(x_out.round(8), y_out.round(8))
    10.0 0.0
    >>> print(abs(x_out - x_in) < 1e-10, abs(y_out - y_in) < 1e-10)
    True True
    >>> # Naive calculation
    >>> import numpy as np
    >>> print(round(-1. * (ra - ra0) * 3600. * np.cos(np.deg2rad(dec0)), 8))
    9.99999993
    >>> print(round((dec - dec0) * 3600., 8))
    -0.00066601
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from numpy import cos, sin, deg2rad
from astropy import wcs


class TangentPlane(object):
    """Class to do tangent plane and inverse tangent plane transformations

    Creates a WCS object for tangent plane projections by creating a FITS
    header and feeding it to astropy

    Parameters
    ----------
    ra0, dec0 : float
        tangent point, i.e. x=0, y=0 in tangent plane (in deg.)
    rot : float
        rotation angle, clockwise from North (in deg.)
    x_scale, y_scale  : float, optional
        plate scale (arcsec per pixel).

    Attributes
    ----------
    w : :class:`~astropy.wcs.WCS`
        a WCS object to store the tangent plane info
    """
    def __init__(self, ra0, dec0, rot, x_scale=-1., y_scale=1.):
        ARCSECPERDEG = 1.0/3600.0

        # make a WCS object with appropriate FITS headers
        self.wcs = wcs.WCS(naxis=2)
        self.wcs.wcs.crpix = [0.0, 0.0]  # central "pixel"
        self.wcs.wcs.crval = [ra0, dec0]  # tangent point
        self.wcs.wcs.ctype = ['RA---TAN', 'DEC--TAN']
        # pixel scale in deg.
        self.wcs.wcs.cdelt = [ARCSECPERDEG * x_scale, ARCSECPERDEG * y_scale]

        # Deal with PA rotation by adding rotation matrix to header
        rrot = deg2rad(rot)
        # clockwise rotation matrix
        self.wcs.wcs.pc = [[cos(rrot), sin(rrot)], [-1.0*sin(rrot), cos(rrot)]]

    def raDec2xy(self, ra, dec):
        """
        Return the x, y position in the tangent
        plane for a given ra, dec

        Parameters
        ----------
        ra, dec : float or array
            the input position (in degrees)

        Returns
        -------
        x, y : array
            the x and y position in arcseconds
        """
        return self.wcs.wcs_world2pix(ra, dec, 1)

    def xy2raDec(self, x, y):
        """
        Return the ra, dec position in the tangent
        plane for a given x, y

        Parameters
        ----------
        x, y : floats or arrays
            the input position (in arcseconds)

        Returns
        -------
        ra, dec : array
            the ra and dec position in degrees
        """
        return self.wcs.wcs_pix2world(x, y, 1)
