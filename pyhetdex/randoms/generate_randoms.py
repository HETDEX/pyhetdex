"""
Module containing functions to generate randoms sources,
measure their noise from a noise map, derive an SNR for 
each by assigning them fluxes from a luminosity function.

AUTHOR(S): Daniel Farrow 2016 (MPE)

"""
from pyhetdex.het.flux_conversions import virus_eff, extinction, flambda_to_electrons

from datetime import datetime
from numpy.random import poisson, random
from astropy.table import Table
from astropy.wcs import WCS

import numpy as np
import logging
import sys
import matplotlib.pyplot as plt
import astropy.io.fits as fits


def random_emission_line_locations(nrands, lmbda_rest=1215.17):
    """
    Generate the on chip locations of emission lines

    Parameters
    ----------
    nrands : int
        the number of randoms to generate
    lmbda_rest : float (optional)
        the rest frame wavelength of the emission line
     
    Returns
    -------
    x, y : float
        the focal plane position relative to the IFU center
        in arcseconds
    z : float
        the objects redshift
    lambda : float
        the lines observed wavelength in the same units as
        lmbda_rest.
    """

    # from Dustin's single-ifu sim
    X_COORD_MAX = 22.88
    X_COORD_MIN = -1*X_COORD_MAX
    X_SIZE = X_COORD_MAX - X_COORD_MIN

    Y_COORD_MAX = 24.24
    Y_COORD_MIN = -1*Y_COORD_MAX
    Y_SIZE = Y_COORD_MAX - Y_COORD_MIN

    Z_RANGE_MIN = 1.99
    Z_RANGE_MAX = 3.45
    Z_SIZE = Z_RANGE_MAX - Z_RANGE_MIN

    # generate the randoms
    # TODO: Use a better random generator than numpy?
    x = random(nrands)*X_SIZE + X_COORD_MIN
    y = random(nrands)*Y_SIZE + Y_COORD_MIN
    z = random(nrands)*Z_SIZE + Z_RANGE_MIN
    lmbda = (z + 1.0)*lmbda_rest

    return x, y, z, lmbda



def generate_randoms(fn_noise_map, fn_out, nrands): 
    """
    Generate random emission lines over the IFU
    and output them, and the noise/fluxfrac at
    the location they land.

    Parameters
    ----------
    fn_noise_map : str 
        the name of a noise map produced by detect
    fn_out : str
        the name of output file. The format is specified
        by the names extension (.fits, .csv and HDF5 supported)
    nrands : int
        the number of randoms to generate    
    """ 

    log = logging.getLogger()

    log.info("Generating {:d} randoms!".format(nrands))

    x, y, z, lmbda = random_emission_line_locations(nrands)

    noise = return_noise(x, y, lmbda, fn_noise_map) 

    if  len(noise) < 1:
        sys.exit(1)
 
    log.info("Saving to file {:s}".format(fn_out))

    data = Table([x, y, z, lmbda, noise], names=('x', 'y', 'z', 'lambda', 'noise_over_fluxfrac'), 
                 meta={'NAME' : 'Randoms for {:s}'.format(fn_noise_map),
                       'DATECRTD' : datetime.now().strftime("%Y-%m-%d %H:%M:%S")})    

    data.write(fn_out)


def return_noise(x, y, lmbda, fn_noise_map):
    """
    Return noise from fn_noise_map and
    x, y, lambda
    
    Parameters
    ----------
    x, y : float
        position wrt to IFU center (arcseconds)
    lmbda : float
        observed wavelength
    fn_noise_map : str
        the file name of the noise datacube
    """

    log = logging.getLogger()

    try:
        with fits.open(fn_noise_map) as hdus:
            datacube = hdus[0].data
            header = hdus[0].header
    except IOError as e:
        log.error("Problem reading file {:e}".format(e))
        return []

    wcs = WCS(header)

    # find the noise at each pixel of the noise map where
    # there's a source
    pixels = np.array(wcs.all_world2pix(x, y, lmbda, 0), dtype=int)
    noise = datacube[pixels[2], pixels[1], pixels[0]]

    return noise


def flux2snr(flux, lmbda, noise, texp=360.0, airmass=1.23):
    
   signal = flambda_to_electrons(flux, lmbda, 360.0) 
   ext_signal = signal*extinction(lmbda, airmass)
 
   return signal/noise


#generate_randoms(sys.argv[1], sys.argv[2], int(sys.argv[3]))

#
# TODO: Move these tests to pytest
#


x, y  = 5.155615014444944, 3.0050500294416693 
rlbda = 1215.7
flbda = 3.14172e-17
z = 3.34149

noise = return_noise(x, y, rlbda*(1.0 + z), 'Noise_detect.fits')
snr = flux2snr(flbda, rlbda*(1.0 + z), noise)

flux_raw = flambda_to_electrons(flbda, rlbda*(1.0 + z), 360.0) # this should be 2360.2 
atm_ext = extinction(rlbda*(1.0 + z), 1.23) # should be 0.835741 
flux_final = atm_ext*flux_raw



print "========== TEST SOURCE 1 ==============="
print z
print flbda
print flux_raw
print atm_ext 
print flux_final
print noise
print snr

rlbda = 1215.7
flbda = 1.21521e-16
z = 2.56898

flux_raw = flambda_to_electrons(flbda, rlbda*(1.0 + z), 360.0) # this should be 2360.2 
atm_ext = extinction(rlbda*(1.0 + z), 1.23) # should be 0.729536
flux_final = atm_ext*flux_raw


print "========== TEST SOURCE 2 ==============="
print flux_raw
print atm_ext
print flux_final


fluxes = []
zs =  np.linspace(2.5, 3.5, num=20)
for z in zs:
    fluxes.append(flambda_to_electrons(flbda, rlbda*(1.0 + z), 360.0))

plt.plot(zs, fluxes)
plt.show()    
