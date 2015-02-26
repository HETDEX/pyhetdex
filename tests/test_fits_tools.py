"""
tests for pyhetdex.tools.files.fits_tools
"""
from __future__ import print_function, absolute_import

from astropy.io.fits import Header
import nose.tools as nt

import pyhetdex.tools.files.fits_tools as ft


def test_wl_to_index():
    "wavelength to index"
    # header
    h_dict = {"CRVAL1": 3500, 'CDELT1': 2}
    h = Header()
    for k, v in h_dict.items():
        h.set(k, v)

    # input and output
    ws = [4001, None]
    results = [250, None]

    for w, r in zip(ws, results):
        yield _w2i, h, w, r


def _w2i(h, w, r):
    """Run ``ft.wavelength_to_index(h, w)`` and compare with result ``r``"""

    out = ft.wavelength_to_index(h, w)
    nt.assert_equal(r, out)
