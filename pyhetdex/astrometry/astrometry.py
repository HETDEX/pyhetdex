from __future__ import absolute_import, print_function

from numpy import rad2deg, deg2rad
from numpy import sin,cos,arctan
import numpy

"""
Examples    
RA0=0.
DEC0=70.
rot = 0.
x_in, y_in = 10.,0.

# multiply by -1 to make positive x point east for 0 Deg rotation 
ifu = IFUASTROM(RA0=RA0, DEC0=DEC0, rot=rot, x_scale= -1, y_scale=1)


RA,DEC = tan_inv(ifu,x_in,y_in)
x,y    = tan_dir(ifu, RA, DEC)
print "x_in, y_in = ", x_in, y_in
print "RA,DEC = ", RA,DEC
print "x,y = ", x,y


print "Naive calculation: "
print "RA-RA0   [\"] = ", -1.*(RA-RA0)*3600. * cos(deg2rad(DEC0))
print "DEC-DEC0 [\"] = ", (DEC-DEC0)*3600. 
print ""
"""

DEGPERRAD = 57.295779513082323

class IFUASTROM:
    """
    Contains the necessary information to translate from
    on-sky RA and DEC coordinates to the IFUASTROM reference system.
    """
    def __init__(self, RA0, DEC0, rot, x_scale = -1., y_scale = 1.):
        """ Zero point. The RA and DEC coordinates that correspond to x=0,y=0
        in the IFUASTROM mapping file. """
        self.RA0      = RA0     
        self.DEC0     = DEC0   
        """ Rotation of the IFUASTROM, measured East of North such that a galaxy with
        a +10 Deg position angle on sky would be aligned with the y-axis in and IFUASTROM
        that is rotated by +10 Deg.""" 
        self.rot      = rot
        """ IFUASTROM plate scale. These parameters are -1 in x and 1 in y if the 
        IFUASTROM mapping file is perfect in arcseconds."""
        self.x_scale  = x_scale 
        self.y_scale  = y_scale 

def tan_dir(IFUASTROM, RA_in, DEC_in):
    """
    Calculates x and y coordinates for positions in the IFUASTROM coordinate frame.
    Stolen boldly from J. Adams finder_chart code.
    see AIPS Memo 27, Greisen 1983 (ftp://ftp.aoc.nrao.edu/pub/software/aips/TEXT/PUBL/AIPSMEMO27.PS)
    Input
   
    IFUASTROM        = object that describes IFUASTROM astrometry 
    RA_in, DEC_in = 1D arrays of RA/DEC coordinates (in ~ degree!)
    
    Returns:
    x_out,y_out = two 1D arrays containing x and y coordinates (in IFUASTROM coordinates, i.e. ~ arcsec).
    """
    RA0, DEC0, rot, x_scale, y_scale = IFUASTROM.RA0, IFUASTROM.DEC0, IFUASTROM.rot, IFUASTROM.x_scale * DEGPERRAD, IFUASTROM.y_scale * DEGPERRAD
    rRA0   = deg2rad(RA0)
    rDEC0  = deg2rad(DEC0)
    rrot   = deg2rad(rot)

    rRA_in  = deg2rad(RA_in)
    rDEC_in = deg2rad(DEC_in)

    # AIPS Memo 27, 3.1.1
    xhat = ( cos(rDEC_in)*sin(rRA_in - rRA0) ) /\
             (sin(rDEC_in)*sin(rDEC0) + cos(rDEC_in)*cos(rDEC0)*cos(rRA_in - rRA0) )
    yhat = (sin(rDEC_in)*cos(rDEC0) - cos(rDEC_in)*sin(rDEC0)*cos(rRA_in - rRA0) )/\
            (sin(rDEC_in)*sin(rDEC0) + cos(rDEC_in) * cos(rDEC0) * cos(rRA_in - rRA0))

    # rotation and scaling
    x =   (xhat) * cos(rrot)*x_scale + (yhat) * sin(rrot)*y_scale
    y = - (xhat) * sin(rrot)*x_scale + (yhat) * cos(rrot)*y_scale
    
    return x*3600.,y*3600. 

def tan_inv(IFUASTROM,x_in,y_in):
    """
    Calculates RA and DEC coordinates for positions in the IFUASTROM coordinate frame.
    Stolen boldly from J. Adams finder_chart code.
    see AIPS Memo 27, Greisen 1983 (ftp://ftp.aoc.nrao.edu/pub/software/aips/TEXT/PUBL/AIPSMEMO27.PS)

    Input
   
    IFUASTROM        = object that descibres IFUASTROM astrometry 
    x_in, y_in = 1D arrays of x/y coordinates (in ~ arcsec!)
    
    Returns:
    RA_out,dec_out = two 1D arrays containing RA and DEC coordinates (in degree).
    """
    RA0, DEC0, rot, x_scale, y_scale = IFUASTROM.RA0, IFUASTROM.DEC0, IFUASTROM.rot, IFUASTROM.x_scale * DEGPERRAD, IFUASTROM.y_scale * DEGPERRAD
    rRA0   = deg2rad(RA0)
    rDEC0  = deg2rad(DEC0)
    rrot   = deg2rad(rot)

    # rotation and scaling
    xhat = (x_in/3600.) * cos(rrot)/x_scale - (y_in/3600.) * sin(rrot)/y_scale
    yhat = (x_in/3600.) * sin(rrot)/x_scale + (y_in/3600.) * cos(rrot)/y_scale

    # AIPS Memo 27, 3.1.2
    rRA_out = rRA0 + arctan(xhat/(cos(rDEC0) - yhat * sin(rDEC0)))
    rDEC_out = arctan(cos(rRA_out - rRA0) * (yhat * cos(rDEC0) + sin(rDEC0))\
                /(cos(rDEC0) - yhat * sin(rDEC0)))

    return rad2deg(rRA_out), rad2deg(rDEC_out)

