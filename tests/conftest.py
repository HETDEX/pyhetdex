"""pytest configurations and global stuff"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import matplotlib
matplotlib.use('Agg')

from astropy.io import fits
import numpy as np

import pytest
import py
import os

collect_ignore = ["setup.py"]


@pytest.fixture(scope="session")
def datadir():
    """ Return a py.path.local object for the test data directory"""
    return py.path.local(os.path.dirname(__file__)).join('data')


def compare_fits(expected, actual, hkeys=[]):
    with fits.open(expected) as e_hdu:
        with fits.open(actual) as a_hdu:
            for h in hkeys:
                assert e_hdu[0].header[h] == a_hdu[0].header[h]

            return np.isclose(e_hdu[0].data, a_hdu[0].data, 8).all()
