"""Tangent plane projection transformation.

The class from this module is a wrapper around :class:`astropy.wcs.WCS`

.. warning::
    This module is temporary.
    The chosen implementation of the tangent plane projection will go into
    :mod:`pyhetdex.coordinates.tangent_projection` and this module will be
    removed

.. moduleauthor:: Daniel Farrow <dfarrow@mpe.mpg.de>
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
    ra0, dec0 : (float)
        tangent point, i.e. x=0, y=0 in tangent plane (in deg.)
    rot : (float)
        rotation angle, clockwise from North (in deg.)

    Attributes
    ----------
    w : :class:`~astropy.wcs.WCS`
        a WCS object to store the tangent plane info
    """
    def __init__(self, ra0, dec0, rot, x_scale=-1, y_scale=1):

        ARCSECPERDEG = 1.0/3600.0

        # make a WCS object with appropriate FITS headers
        self.w = wcs.WCS(naxis=2)
        self.w.wcs.crpix = [0.0, 0.0]  # central "pixel"
        self.w.wcs.crval = [ra0, dec0]  # tangent point
        self.w.wcs.ctype = ['RA---TAN', 'DEC--TAN']
        # pixel scale in deg.
        self.w.wcs.cdelt = [ARCSECPERDEG * x_scale, ARCSECPERDEG * y_scale]

        # Deal with PA rotation by adding rotation matrix to header
        rrot = deg2rad(rot)
        # clockwise rotation matrix
        self.w.wcs.pc = [[cos(rrot), sin(rrot)], [-1.0*sin(rrot), cos(rrot)]]

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
        return self.w.wcs_world2pix(ra, dec, 1)

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
        return self.w.wcs_pix2world(x, y, 1)
