"""pytest configurations and global stuff"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from distutils.spawn import find_executable

import matplotlib
matplotlib.use('Agg')

from astropy.io import fits
import numpy as np

import pytest
import py
import os

collect_ignore = ["setup.py"]


@pytest.fixture
def clear_tmpdir(tmpdir):
    '''Remove ``tmpdir`` after the test is done. Useful for tests that produce
    a lot of data'''
    yield
    tmpdir.remove(rec=True)


@pytest.fixture(scope="session")
def datadir():
    """ Return a py.path.local object for the test data directory"""
    return py.path.local(os.path.dirname(__file__)).join('data')


@pytest.fixture
def dither_fast(datadir):
    'Returns the dither fast file as a py.path.local object'
    return datadir.join("dither_fast_SIMDEX-4000-obs-1_046.txt")


@pytest.fixture
def ifucenter_file(datadir):
    'Returns the ifu center file file as a py.path.local object'
    return datadir.join("IFUcen_HETDEX.txt")


@pytest.fixture(scope='session')
def dither_wrong(datadir):
    """Returns the path to the dither_wrong file"""
    return datadir.join("dither_wrong_SIMDEX-4000-obs-1_046.txt")


@pytest.fixture(scope='session')
def example_fdither(datadir):
    """Returns the path to the dither.example.txt file"""
    return datadir.join('dither.example.txt')


@pytest.fixture(scope='session')
def ditherpos_file(datadir):
    """Returns the path to the dither_positions.txt file"""
    return datadir.join("dither_positions.txt")


@pytest.fixture(scope='session')
def fplane_file(datadir):
    """Returns the path to the fplane.txt file"""
    return datadir.join('fplane.txt')


@pytest.fixture(scope='session')
def dither_file(datadir):
    return datadir.join("dither_SIMDEX-4000-obs-1_046.txt")


@pytest.fixture(scope='session')
def dither_other(datadir):
    return datadir.join("dither_other_SIMDEX-4000-obs-1_046.txt")


@pytest.fixture(scope='session')
def ifucenter_missf(datadir):
    return datadir.join("IFUcen_HETDEX_missf.txt")


@pytest.fixture
def cont_detection(datadir):
    'Returns a continuum detection file as a py.path.local object'
    return datadir.join('detect046_cont.dat')


@pytest.fixture
def line_detection(datadir):
    'Returns a line detection file as a py.path.local object'
    return datadir.join('detect085_line.dat')


@pytest.fixture
def sigmafile(datadir):
    'return the sigma file as a py.path.local instance'
    return datadir.join("Sigma_test_data.fits")


@pytest.fixture
def detfracfluxfile(datadir):
    'return the fraction flux file as a py.path.local instance'
    return datadir.join("DetAperFluxFrac_test_data.fits")


@pytest.fixture
def randoms(datadir):
    'return the random test data file as a py.path.local instance'
    return datadir.join("Randoms_test_data.fits")


@pytest.fixture
def compare_fits():
    '''Return a function that compare fits files'''
    def _compare_fist(expected, actual, hkeys=[]):
        with fits.open(expected) as e_hdu, fits.open(actual) as a_hdu:
            for h in hkeys:
                assert e_hdu[0].header[h] == a_hdu[0].header[h]

            return np.isclose(e_hdu[0].data, a_hdu[0].data, 8).all()
    return _compare_fist


@pytest.fixture
def skip_if_no_executable():
    '''return a function that skips if the executable is not found in the path
    or CUREBIN'''

    def _skip_executable(exename):
        fullexe = find_executable(exename)
        if fullexe is None:
            fullexe = find_executable(exename,
                                      path=os.environ.get('CUREBIN', ''))
        if fullexe is None:
            pytest.skip('Executable "{}" not found'.format(exename))

        return fullexe
    return _skip_executable
