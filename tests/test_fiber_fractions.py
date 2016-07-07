""" Test pyhetdex.cure.fiber_fractions"""
from __future__ import (print_function, absolute_import)

import pytest
from pyhetdex.cure.fiber_fractions import FiberFracMap


@pytest.fixture(scope='session')
def example_fdither(datadir):
    """Returns the path to the dither.example.txt file"""
    return datadir.join('dither.example.fiberfrac.txt')


@pytest.fixture(scope='session')
def example_ifucen(datadir):
    """Returns the path to the dither.example.txt file"""
    return datadir.join('IFUcen_HETDEX.fiberfrac.txt')


def test_fiberfrac(example_ifucen, example_fdither):

    fiber_map = FiberFracMap(str(example_ifucen), str(example_fdither),
                             psf_type="moffat")
    afrac, _, afluxfrac, _, _ = fiber_map.return_fiberfrac([-11.391],
                                                           [-9.5263], 1.4)
    bfrac, _, bfluxfrac, _, _ = fiber_map.return_fiberfrac([0.62042],
                                                           [0.0014127], 1.4)
    cfrac, _, cfluxfrac, _, _ = fiber_map.return_fiberfrac([0.27201], [21.141],
                                                           1.4)

    # comparisons to Cure values, ensure within 5%
    assert abs(afrac - 3.03045)/3.03045 < 0.05
    assert abs(bfrac - 3.18579)/3.18579 < 0.05
    assert abs(cfrac - 3.30476)/3.30476 < 0.05
    assert abs(afluxfrac - 0.677412)/0.677412 < 0.05
    assert abs(bfluxfrac - 0.731427)/0.677412 < 0.05
    assert abs(cfluxfrac - 0.796093)/0.677412 < 0.05
