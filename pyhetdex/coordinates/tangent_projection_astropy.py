"""Tangent plane projection transformation

.. moduleauthor:: Daniel Farrow <dfarrow@mpe.mpg.de>


Examples
--------

Example of use of this module::

    >>> ra0 = 0.
    >>> dec0 = 70.
    >>> rot = 0.
    >>> x_in, y_in = 10., 0.
    >>> tp = TangentPlane(ra0, dec0, rot)
    >>> ra, dec = tp.xy2raDec(x_in, y_in)
    >>> x_out, y_out = tp.raDec2xy(ra, dec)
    >>> ra, dec
    (-0.0081216788349454117, 69.999999814997963)
    >>> x_out, y_out
    (9.9999999999999964, 2.2899993733449891e-11)
 

"""

from __future__ import absolute_import

from numpy import cos, sin, deg2rad
from astropy import wcs

class TangentPlane(object):
    """ Class to do tangent plane and inverse tangent plane 
        transformations

        Creates a WCS object for tangent plane projections 
        by creating a FITS header and feeding it to astropy

        Parameters
        ----------
        ra0, dec0 : (float)
            tangent point, i.e. x=0, y=0 in tangent plane (in deg.)
        rot : (float)
            rotation angle, clockwise from North (in deg.)

        Attributes
        ----------
        w : astropy.wcs.WCS 
            a WCS object to store the tangent plane info
     
    """

    def __init__(self, ra0, dec0, rot):

        ARCSECPERDEG = 1.0/3600.0

        # make a WCS object with appropriate FITS headers
        self.w = wcs.WCS(naxis=2)
        self.w.wcs.crpix = [0.0, 0.0] # central "pixel"
        self.w.wcs.crval = [ra0, dec0] # tangent point
        self.w.wcs.ctype = ['RA---TAN', 'DEC--TAN']
        self.w.wcs.cdelt = [ARCSECPERDEG, ARCSECPERDEG] # pixel scale in deg.
     
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
        if type(ra) == float:
            coords = [[ra, dec]]
        else:
            coords = zip(ra, dec)

        out = self.w.wcs_world2pix(coords, 1)

        x = out[:, 0]
        y = out[:, 1]            

        return x, y

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
        if type(x) == float:
            coords = [[x, y]]
        else:
            coords = zip(x, y)

        out = self.w.wcs_pix2world(coords, 1)    

        ra = out[:, 0]
        dec = out[:, 1] 
 
        return ra, dec















