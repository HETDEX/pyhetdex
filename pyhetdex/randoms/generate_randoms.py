# Misc python library to support HETDEX software and data analysis
# Copyright (C) 2016  "The HETDEX collaboration"
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
Module containing functions to generate randoms sources,
measure their noise from a noise map, derive an SNR for
each by assigning them fluxes from a luminosity function.

AUTHOR(S): Daniel Farrow 2016 (MPE)

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime
from numpy.random import random
from numpy.polynomial import polynomial as poly
from astropy.table import Table, hstack
from astropy.wcs import WCS

import numpy as np
import logging
import sys
import astropy.io.fits as fits

from pyhetdex.het.flux_conversions import (virus_eff, extinction,
                                           flambda_to_electrons)
from pyhetdex.randoms.luminosity_functions import FlatLuminosityFunction


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


def generate_randoms(fn_variance_map, fn_detaper_fluxfrac, fn_out, nrands):
    """
    Generate random emission lines over the IFU
    and output them, and the noise/fluxfrac at
    the location they land.

    Parameters
    ----------
    fn_variance_map : str
        the name of a variance map produced by detect
    fn_detaper_fluxfrac :
        the name of a fraction of flux in detection aperture
        map from detect
    fn_out : str
        the name of output file. The format is specified
        by the names extension (.fits, .csv and HDF5 supported)
    nrands : int
        the number of randoms to generate
    """

    log = logging.getLogger()

    msg = "Generating {:d} randoms from files {:s} and {:s} !"
    log.info(msg.format(nrands, fn_variance_map, fn_detaper_fluxfrac))

    x, y, z, lmbda = random_emission_line_locations(nrands)

    variance = return_cube_value(x, y, lmbda, fn_variance_map)
    detaper_fluxfrac = return_cube_value(x, y, lmbda, fn_detaper_fluxfrac)

    if len(variance) < 1:
        sys.exit(1)

    log.info("Saving to file {:s}".format(fn_out))

    data = Table([x, y, z, lmbda, variance, detaper_fluxfrac],
                 names=('x', 'y', 'z', 'lambda', 'variance',
                        'detaper_fluxfrac'),
                 meta={'NAME': 'Randoms for {:s}'.format(fn_variance_map),
                       'DATECRTD': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    data.write(fn_out)


def return_cube_value(x, y, lmbda, fn_cube):
    """
    Return value from fn_cube at
    x, y, lambda

    Parameters
    ----------
    x, y : float
        position wrt to IFU center (arcseconds)
    lmbda : float
        observed wavelength
    fn_cube : str
        the file name of the datacube
    """

    log = logging.getLogger()

    try:
        with fits.open(fn_cube) as hdus:
            datacube = hdus[0].data
            header = hdus[0].header
    except IOError as e:
        log.error("Problem reading file %s", e)
        return []

    wcs = WCS(header)

    # find the noise at each pixel of the noise map where
    # there's a source
    pixels = np.array(wcs.all_world2pix(x, y, lmbda, 0), dtype=int)
    value = datacube[pixels[2], pixels[1], pixels[0]]

    return value


def lum2snr(lum, lmbda, variance, detaper_fluxfrac, texp=360.0, airmass=1.23):
    """
    Return the SNR predicted for a particular
    luminosity. Applies the atmospheric extinction, VIRUS,
    HET efficiency and aperture effects to fluxes.

    Parameters
    ----------
    lum : float
        the luminosity
    lmbda : float
        the wavelength in Angstroms
    variance : float
        the variance in CCD counts
    detaper_fluxfrac : float
        the fraction of total flux within the
        detection aperture
    """

    signal = flambda_to_electrons(lum, lmbda, 360.0)
    ext_signal = detaper_fluxfrac * extinction(lmbda, airmass) *\
        virus_eff(lmbda) * signal

    # remember to count source noise
    return ext_signal/np.sqrt(variance + ext_signal)


def generate_randoms_cmd(args=None):
    """ Command line interface to generate_randoms """
    import argparse

    logging.basicConfig(level=logging.INFO)

    if not args:
        import sys
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='''Generate a catalogue of
                                     randoms''')
    parser.add_argument('fn_variance_map', type=str,
                        help='Filename of a detect variance cube')
    parser.add_argument('fn_detaper_fluxfrac', type=str,
                        help="""Filename of a datcube cube containing the
                        fraction of flux in detection aperture from detect.""")

    parser.add_argument('fn_out', type=str,
                        help='Output filename (extension sets filetype)')
    parser.add_argument('nrands', type=int,
                        help='Number of randoms to generate')

    o = parser.parse_args(args)

    generate_randoms(o.fn_variance_map, o.fn_detaper_fluxfrac, o.fn_out,
                     o.nrands)


def add_fluxes_and_snr_to_randoms_cmd(args=None):
    """ Command line interface to add_fluxes_and_snr_to_randoms """
    import argparse

    logging.basicConfig(level=logging.INFO)

    if not args:
        import sys
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='''Add fluxes and SNR to a
                                     random catalogue.''')
    parser.add_argument('fn_in', type=str,
                        help='Output filename (extension sets filetype)')
    parser.add_argument('fn_out', type=str,
                        help='Output filename (extension sets filetype)')
    parser.add_argument('--det-eff', action='store_true',
                        help="Apply detection efficiency effects")

    o = parser.parse_args(args)

    add_fluxes_and_snr_to_randoms(o.fn_in, o.fn_out,
                                  apply_detection_eff=o.det_eff)


def detection_efficiency(snr):
    """
    Return probablity of detection given
    an input SNR

    Parameters
    ----------
    snr : float
        Signal to noise ratio of LAE

    Returns
    -------
    p : float
        probability of detection of an LAE
    """

    coeffs = [1.23654837e-01,   3.18302562e-01, 1.58954868e-01,
              -1.16370722e-01, 2.66873455e-02,  -2.71750060e-03,
              1.04901142e-04]

    # Cut to avoid extrapolating polynomial fit to detected fraction too far
    if snr < 2.5:
        return 0.0
    elif snr > 7.0:
        return 1.0
    else:
        return poly.polyval(snr - 3.0, coeffs)


def add_fluxes_and_snr_to_randoms(fn_randoms, fn_out,
                                  apply_detection_eff=True):
    """
    Read in a set of randoms from generate_randoms, and
    assign fluxes and SNR values to the randoms based
    on some luminosity function

    Parameters
    ----------
    fn_randoms, fnout : str
        filename of randoms and output file

    """

    log = logging.getLogger()

    # parameters for Dustin's simulation
    lf = FlatLuminosityFunction(3.0e-17, 2.5e-16)

    try:
        table = Table.read(fn_randoms)

    except IOError as e:

        log.error("Problem reading file {:s}".format(fn_randoms))
        log.error(e)

    lum = []
    snr = []
    de = []
    rs = []
    to_remove = []

    for i, source in enumerate(table):

        # Generate a random flux from the LF
        tlum = lf.inverse_normed_cumulative(random())
        tsnr = lum2snr(tlum, source['lambda'], source['variance'],
                       source['detaper_fluxfrac'])

        # apply detection efficiency
        r = random()
        deff = detection_efficiency(tsnr)
        if r > deff and apply_detection_eff:
            to_remove.append(i)
        else:
            lum.append(tlum)
            snr.append(tsnr)
            de.append(deff)
            rs.append(random())

    table.remove_rows(to_remove)
    table_snr = Table([lum, snr, de, rs],
                      names=('flambda', 'SNR', 'det_eff', "random"))
    table_out = hstack([table, table_snr])
    table_out.write(fn_out)
