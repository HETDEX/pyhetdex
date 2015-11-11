"""
Test the various pieces of the image quality fit
"""

from __future__ import absolute_import

import os

import numpy as np

from pyhetdex.tools.astro import iq_fit

import settings as s

dither_fast = os.path.join(s.datadir, "dither_fast_SIMDEX-4000-obs-1_046.txt")
ifucenter_file = os.path.join(s.datadir, "IFUcen_HETDEX.txt")
detection = os.path.join(s.datadir, 'detect046_cont.dat')


def test_iq_fit():
    "Test the fit of the image quality"
    # get the first star from the detection file
    xy = np.loadtxt(detection, usecols=[1, 2])[0, :]
    bestfit, = iq_fit.fit_image_quality(dither_fast, ifucenter_file,
                                        stars=[xy], wmin=4000., wmax=5000.)

    print(bestfit)

    # TODO: check it carefully
    assert round(xy[0] - bestfit[1], 0) == 0
    assert round(xy[1] - bestfit[2], 0) == 0
