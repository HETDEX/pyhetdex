"""
Test pyhetdex/astrometry/astrometry.py
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pytest

import pyhetdex.coordinates.tangent_projection as tp


@pytest.fixture
def ifuastrom():
    """return a pyhetdex.coordinates.tangent_projection.IFUAstrom instance"""
    ra0 = 0.
    dec0 = 70.
    rot = 0.
    return tp.TangentPlane(ra0=ra0, dec0=dec0, rot=rot, x_scale=-1, y_scale=1)


@pytest.fixture
def x_y_in():
    "returns input x and y."
    return 10., 0.


@pytest.fixture
def x_y_exp():
    "returns expected x and y."
    return -1044561.64704, -566707.897592


@pytest.fixture
def ra_dec_in():
    "returns input ra and dec"
    return 60, 0.


@pytest.fixture
def ra_dec_exp():
    "returns expected ra and dec"
    return -0.00812167883495, 69.999999815


def test_tan_dir(ifuastrom, ra_dec_in, x_y_exp):
    "Test the direct transform"
    x, y = ifuastrom.raDec2xy(*ra_dec_in)
    exp_x, exp_y = x_y_exp
    assert round(exp_x - x, 5) == 0
    assert round(exp_y - y, 5) == 0


def test_tan_inv(ifuastrom, x_y_in, ra_dec_exp):
    "Test the inverse transform"
    ra, dec = ifuastrom.xy2raDec(*x_y_in)
    exp_ra, exp_dec = ra_dec_exp
    assert round(exp_ra - ra, 10) == 0
    assert round(exp_dec - dec, 10) == 0


def test_tan_dirinv(ifuastrom, ra_dec_in):
    """Test chaining the direct and inverse transform"""
    ra_in, dec_in = ra_dec_in
    x, y = ifuastrom.raDec2xy(ra_in, dec_in)
    ra, dec = ifuastrom.xy2raDec(x, y)
    assert round(ra_in - ra, 10) == 0
    assert round(dec_in - dec, 10) == 0


def test_tan_invdir(ifuastrom, x_y_in):
    """Test chaining the inverse and direct transform"""
    x_in, y_in = x_y_in
    ra, dec = ifuastrom.xy2raDec(x_in, y_in)
    x, y = ifuastrom.raDec2xy(ra, dec)
    assert np.isclose(x_in, x)
    assert np.isclose(y_in, y)
