"""
tests for pyhetdex.randoms.generate_randoms
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import astropy.io.fits as fits

import pyhetdex.randoms.generate_randoms as gr


def test_generate_randoms_cmd(tmpdir, sigmafile, detfracfluxfile):
    """test command line tool to generate randoms"""
    test_cat = tmpdir.join("TestCat.fits")
    args = [sigmafile.strpath, detfracfluxfile.strpath, test_cat.strpath,
            '100']
    gr.generate_randoms_cmd(args=args)

    with test_cat.open('rb') as fp:
        data, header = fits.getdata(fp, header=True)
        assert header["NAXIS2"] == 100, "catalogue of the wrong length"
        assert all(np.isfinite(data["x"]))
        assert all(np.isfinite(data["y"]))
        assert all(np.isfinite(data["z"]))


def test_fluxes_and_snr_to_randoms_cmd(tmpdir, randoms):
    """test command line tool to add flux and snr to randoms"""
    test_cat = tmpdir.join("TestCat.fits")
    args = [randoms.strpath, test_cat.strpath, '--det-eff']
    gr.add_fluxes_and_snr_to_randoms_cmd(args=args)

    with test_cat.open('rb') as fp:
        data, header = fits.getdata(fp, header=True)
        assert header["NAXIS2"] > 0
        assert all(np.isfinite(data["flambda"]))
        assert all(data["random"] > -0.001)
        assert all(data["random"] < 1.001)
        assert all(data["det_eff"] > -0.001)
        assert all(data["det_eff"] < 1.001)
