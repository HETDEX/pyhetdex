"""
Module to deal with converting between flux and
counts on the detector

"""

import numpy as np
import matplotlib.pyplot as plt


def virus_eff(lbda):
    """
    Model fit to Virus + HET + atmosphere efficiency

    Parameters
    ----------
    lbda : float
        wavelength in Angstroms

    Returns
    -------
    virus_eff : float
        the efficiency of Virus + HET + atmos
    """

    l = lbda/1000.0
    return (-4.2490646 + 2.7864084*l - 0.57810372*l*l + 0.039241072*l*l*l)

def extinction(lbda, airmass):
    """
    Model fit to the atmospheric detection,
    taken from projector.cpp (automatically applied
    to input/output fluxes in Cure).

    Parameters
    ----------
    lbda : float
        wavelength in Angstroms
    airmass : float

    """   
 
    lam = lbda / 1000.0

    l2 = lam*lam
    l3 = l2*lam
    l4 = l2*l2
    l5 = l2*l3
    l6 = l3*l3
    l7 = l3*l4

    ext_mag = -323.131 + 481.712*lam - 303.375*l2 + 105.294*l3 - 21.8203*l4 \
              + 2.70452*l5 - 0.185798*l6 + 0.00545958*l7 

    ext = np.power(10.0, -0.4*ext_mag*airmass)

    return ext


def flambda_to_electrons(flbda, lbda, tint):
    """
    Convert flux to electrons assuming a 10 m clear aperture. Also taken
    from Cure.

    Parameters
    ----------
    flbda : float
        flux / lambda
    lbda : float
        wavelength
    tint : float
        exposure time 
    """

    h = 1.054572e-34*2.*np.pi*1e7 # Planck's constant in erg
    c = 2.997925e+18; # c in A/s
    nu = c/lbda;
    A = np.pi*(10.0/2.*100.)*(10.0/2.*100.); #10m clear aperture in cm^2

    #number of detected electrons for an object of spectrum flambda
    return A*tint*flbda/(h*nu)

