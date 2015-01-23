"""
Test pyhetdex.tools.analysis.sky
"""

from __future__ import print_function

import itertools as it
import os
import warnings

from astropy.io import fits
import numpy as np

from pyhetdex.tools.analysis import sky
from pyhetdex.common.file_tools import prefix_filename

import settings as s

fname_template = os.path.join(s.datadir, "jpes20120301T000000_046L_sci.fits")
fname = prefix_filename(fname_template, "Fe")
skysub_fname = prefix_filename(fname_template, 'SFe')
sky_fname = prefix_filename(fname_template, 'SkyFe')
skysub_ref = prefix_filename(fname_template, 'FeS')
sky_ref = prefix_filename(fname_template, 'FeSky')


def test_sky_substraction():
    "Test the sky subtraction"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for ws, wl, w in it.product([3800, 4500], [4500, 5200], [10, 20, 30]):
            if ws < wl:
                yield sky_sub, fname, ws, wl, w


def sky_sub(fname, wmin, wmax, width):
    "do the actual sky subtraction and test"
    sky.fe_sky_subtraction(fname, wmin=wmin, wmax=wmax, width=width)
    # compare the outputs with the reference
    diffS = fits_difference(skysub_fname, skysub_ref)
    diffSky = fits_difference(sky_fname, sky_ref)
    msg = "wmin: {ws:d}, wmax: {wl:d}, width: {w:d}."
    msg += " Skysub: {ss:> 8.2%}; sky: {s:> 8.2%}"
    print(msg.format(ss=diffS, s=diffSky, ws=wmin, wl=wmax, w=width))


def fits_difference(fname1, fname2):
    """
    get the data of the fits, do the difference and return the average
    fractional difference of the first with respect to the second:
    mean(data1/data2 - 1)
    """
    data1 = np.nanmean(fits.getdata(fname1)[:, 200:-200])
    data2 = np.nanmean(fits.getdata(fname2)[:, 200:-200])
    # data1 = fits.getdata(fname1)[:, 200:-200]
    # data2 = fits.getdata(fname2)[:, 200:-200]
    # print(data1, data2, data1/data2)
    return data1/data2 - 1.
    # return np.nanmedian(data1/data2 - 1.)
