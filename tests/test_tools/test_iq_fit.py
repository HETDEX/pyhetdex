"""
Test the various pieces of the image quality fit
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from pyhetdex.tools.astro import iq_fit


def test_iq_fit(dither_fast, ifucenter_file, detection):
    "Test the fit of the image quality"
    # get the first star from the detection file
    xy = np.loadtxt(detection.strpath, usecols=[1, 2])[0, :]
    bestfit, = iq_fit.fit_image_quality(dither_fast.strpath,
                                        ifucenter_file.strpath,
                                        stars=[xy], wmin=4000., wmax=5000.)

    # TODO: check it carefully
    assert round(xy[0] - bestfit[1], 0) == 0
    assert round(xy[1] - bestfit[2], 0) == 0
