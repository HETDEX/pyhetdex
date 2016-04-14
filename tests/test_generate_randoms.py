"""
tests for pyhetdex.randoms.generate_randoms
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import numpy as np
import settings
import pytest
import astropy.io.fits as fits

import pyhetdex.randoms.generate_randoms as gr

sigmafile = os.path.join(settings.datadir, "Sigma_test_data.fits") 
detfracfluxfile = os.path.join(settings.datadir, "DetAperFluxFrac_test_data.fits") 
randoms = os.path.join(settings.datadir, "Randoms_test_data.fits")

def test_generate_randoms_cmd(tmpdir):
    """test command line tool to generate randoms"""
    test_cat = str(tmpdir.join("TestCat.fits"))
    args = [sigmafile, detfracfluxfile, test_cat, '100']
    gr.generate_randoms_cmd(args=args)

    with open(test_cat, 'rb') as fp:
        data, header = fits.getdata(fp, header=True)
        assert header["NAXIS2"] == 100, "produced catalogue is the wrong length"
        assert (all(np.isfinite(data["x"])) and all(np.isfinite(data["y"]))), \
               "some of the x, y values are not finite!" 
        assert all(np.isfinite(data["z"])), "some of the redshifts are not finite!"



def test_fluxes_and_snr_to_randoms_cmd(tmpdir):
    """test command line tool to add flux and snr to randoms"""
    test_cat = str(tmpdir.join("TestCat.fits"))
    args = [randoms, test_cat, '--det-eff']
    gr.add_fluxes_and_snr_to_randoms_cmd(args=args)

    with open(test_cat, 'rb') as fp:
        data, header = fits.getdata(fp, header=True)
        assert header["NAXIS2"] > 0, "produced catalogue has no entries"
        assert all(np.isfinite(data["flambda"])), "some of the flambda are not finite!" 
        assert all(data["random"] > -0.001) and all(data["random"] < 1.001), \
               "random values out of range" 
        assert all(data["det_eff"] > -0.001) and all(data["det_eff"] < 1.001), \
               "detection efficiency values out of range" 
      





