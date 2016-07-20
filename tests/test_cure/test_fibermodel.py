"Test pyhetdex.cure.fibermodel"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pyhetdex.cure.fibermodel as fib
import pytest
import numpy as np


@pytest.fixture(scope='module', params=['fibermodel_16.fmod',
                                        'fibermodel_17.fmod',
                                        'fibermodel_18.fmod',
                                        'fibermodel_19.fmod',
                                        'fibermodel_21.fmod'])
def fmod(datadir, request):
    'return a fiber model'
    return fib.FiberModel(datadir.join(request.param).strpath)


class TestFibermodel(object):
    def test_version(self, fmod):
        expected = fmod.filename.split('.')[-2].split('_')[-1]
        assert fmod.version == int(expected)

    def test_fiducial(self, fmod):
        if fmod.version < 18:
            assert fmod.fiducial_fib_ == 110
        else:
            pass

    def test_exp(self, fmod):
        if fmod.version == 19:
            assert np.isclose(fmod.exp_par_.data[0], -0.64074877344398939)
        elif fmod.version == 21:
            assert np.isclose(fmod.exp_par_.data[0], 0.85160073745336118)
        else:
            pass

    def test_wings(self, fmod):
        if fmod.version >= 21:
            assert np.isclose(fmod.powerlaw_wings[0], 0.0004)
            assert np.isclose(fmod.powerlaw_wings[3], 1.)
        else:
            pass

    def test_ampsize(self, fmod):
        if fmod.version < 19:
            assert len(fmod.amplitudes) == 224
        else:
            assert len(fmod.amplitudes) == 223

    def test_wrong_version(self, datadir):
        with pytest.raises(Exception):
            fib.FiberModel(datadir.join('fibermodel_14.fmod').strpath)
