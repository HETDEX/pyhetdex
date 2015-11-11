"""
tests for pyhetdex.tools.files.fits_tools
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from astropy.io.fits import Header
import pytest

import pyhetdex.tools.files.fits_tools as ft


@pytest.mark.parametrize('ws, result',
                         [(4001, 250), (None, None)])
def test_wl_to_index(ws, result):
    "wavelength to index"
    # header
    h_dict = {"CRVAL1": 3500, 'CDELT1': 2}
    h = Header()
    for k, v in h_dict.items():
        h.set(k, v)
    out = ft.wavelength_to_index(h, ws)
    assert out == result
