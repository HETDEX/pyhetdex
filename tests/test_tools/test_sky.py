"""
Test pyhetdex.tools.analysis.sky
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from astropy.io import fits
import numpy as np
import py
import pytest

from pyhetdex.tools.astro import sky
from pyhetdex.tools.files.file_tools import prefix_filename


wls = [3800, 4500, 5200]
# wls = [3600, 4000, 4500, 5000, 5400]


@pytest.fixture
def fname_template(datadir):
    """Template for joined file names"""
    return datadir.join("jpes20120301T000000_046L_sci.fits").strpath


@pytest.fixture
def fname(tmpdir, fname_template):
    """Copy the Fe file into a temporary directory and return the file name"""
    fe_name = py.path.local(prefix_filename(fname_template, "Fe"))
    fe_name.copy(tmpdir)

    fe_name = tmpdir.join(fe_name.basename)

    return str(fe_name)


@pytest.fixture
def outfiles(fname):
    """Subtracted and sky output file name"""
    skysub_fname = prefix_filename(fname, 'S')
    sky_fname = prefix_filename(fname, 'Sky')
    return skysub_fname, sky_fname


@pytest.fixture
def reffiles(fname_template):
    """Subtracted and sky reference file name"""
    skysub_ref = prefix_filename(fname_template, 'FeS')
    sky_ref = prefix_filename(fname_template, 'FeSky')
    return skysub_ref, sky_ref


@pytest.mark.parametrize('wmin', wls[:-1])
@pytest.mark.parametrize('wmax', wls[1:])
@pytest.mark.parametrize('width', [10, 20, 30])
def test_sky_sub(clear_tmpdir, fname, outfiles, reffiles, wmin, wmax, width):
    "do the actual sky subtraction and test"
    if wmin == wmax:
        pytest.skip("wmin == wmax")
    sky.fe_sky_subtraction(fname, wmin=wmin, wmax=wmax, width=width)
    # compare the outputs with the reference
    diffS = fits_difference(outfiles[0], reffiles[0])
    diffSky = fits_difference(outfiles[1], reffiles[0])
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


@pytest.mark.parametrize('wmin', wls[:-1])
@pytest.mark.parametrize('wmax', wls[1:])
def test_sky_bkg(clear_tmpdir, fname, wmin, wmax):
    "Test the sky background estimation"
    if wmin == wmax:
        pytest.skip("wmin == wmax")
    # do the sky subtraction
    sky.fe_sky_background(fname, wmin=wmin, wmax=wmax)
