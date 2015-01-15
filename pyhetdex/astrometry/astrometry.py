"""
Examples:
ra0 = 0.
dec0 = 70.
rot = 0.
x_in, y_in = 10., 0.

# multiply by -1 to make positive x point east for 0 Deg rotation
ifu = IFUAstrom(ra0=ra0, dec0=dec0, rot=rot, x_scale= -1, y_scale=1)


ra, dec = tan_inv(ifu, x_in, y_in)
x, y    = tan_dir(ifu, ra, dec)
print("x_in, y_in = ", x_in, y_in)
print("ra, dec = ", ra, dec)
print("x, y = ", x, y)


print("Naive calculation: ")
print("ra - ra0   [\"] = ", -1. * (ra - ra0) * 3600. * cos(deg2rad(dec0)))
print("dec - dec0 [\"] = ", (dec - dec0) * 3600.)
"""

from __future__ import absolute_import, print_function

import numpy as np


DEGPERRAD = 57.295779513082323


class IFUAstrom(object):
    """
    Contains the necessary information to translate from
    on-sky RA and DEC coordinates to the IFUASTROM reference system.
    """
    def __init__(self, ra0, dec0, rot, x_scale=-1., y_scale=1.):
        """
        Zero point.
        Parameters
        ----------
        ra0, dec0: floats
            ra and dec coordinated that correspond to x=0,y=0 in the IFUASTROM
            mapping file.
        rot: float
            Rotation of the IFUASTROM, measured East of North such that a
            galaxy with a +10 Deg position angle on sky would be aligned with
            the y-axis in and IFUASTROM that is rotated by +10 Deg.
        x_scale, y_scale: floats
            IFUASTROM plate scale. These parameters are -1 in x and 1 in y if
            the IFUASTROM mapping file is perfect in arcseconds.
        """
        self.ra0 = ra0
        self.dec0 = dec0
        self.rot = rot
        self.x_scale = x_scale
        self.y_scale = y_scale


def tan_dir(ifuastrom, ra_in, dec_in):
    """
    Calculate x and y coordinates for positions in the IFUASTROM coordinate
    frame. Stolen boldly from J. Adams finder_chart code.
    see AIPS Memo 27, Greisen 1983
    (ftp://ftp.aoc.nrao.edu/pub/software/aips/TEXT/PUBL/AIPSMEMO27.PS)
    Parameters
    ----------
    ifuastrom: IFUAstrom instance
        describes IFUASTROM astrometry
    ra_in, dec_in: 1D arrays
        RA/DEC coordinates (in degree!)
    output
    ------
    x_out, y_out: 1D arrays
        x and y coordinates (in IFUASTROM coordinates, i.e. arcsec).
    """
    ra0, dec0 = ifuastrom.ra0, ifuastrom.dec0
    rot = ifuastrom.rot
    x_scale = ifuastrom.x_scale * DEGPERRAD
    y_scale = ifuastrom.y_scale * DEGPERRAD

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


def tan_inv(ifuastrom, x_in, y_in):
    """
    Calculates RA and DEC coordinates for positions in the IFUASTROM coordinate
    frame.  Stolen boldly from J. Adams finder_chart code.  see AIPS Memo 27,
    Greisen 1983
    (ftp://ftp.aoc.nrao.edu/pub/software/aips/TEXT/PUBL/AIPSMEMO27.PS)
    Parameters
    ----------
    ifuastrom: IFUAstrom instance
        describes IFUASTROM astrometry
    x_in, y_in: 1D arrays
        x and y coordinates (in IFUASTROM coordinates, i.e. arcsec).
    output
    ------
    ra_out, dec_out: 1D arrays
        RA/DEC coordinates (in degree!)
    """
    ra0, dec0 = ifuastrom.ra0, ifuastrom.dec0
    rot = ifuastrom.rot
    x_scale = ifuastrom.x_scale * DEGPERRAD
    y_scale = ifuastrom.y_scale * DEGPERRAD

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
