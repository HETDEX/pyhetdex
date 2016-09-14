"Test pyhetdex.cure.fibermodel"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pyhetdex.cure.fibermodel as fib
import pyhetdex.cure.distortion as dist
import pytest
import numpy as np


@pytest.fixture(scope='module', params=['fibermodel_16.fmod',
                                        'fibermodel_17.fmod',
                                        'fibermodel_18.fmod',
                                        'fibermodel_19.fmod',
                                        'fibermodel_21.fmod',
                                        'fibermodel_22.fmod'])
def fmod(datadir, request):
    'return a fiber model'
    return fib.FiberModel(datadir.join(request.param).strpath)

testprecision = 1.e-4


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
        elif fmod.version >= 19 and fmod.version < 22:
            assert len(fmod.amplitudes) == 223
        else:
            assert len(fmod.amplitudes) == 224

    def test_wrong_version(self, datadir):
        with pytest.raises(Exception):
            fib.FiberModel(datadir.join('fibermodel_14.fmod').strpath)

    def test_single_fiberflux(self, datadir, fmod):
        if fmod.version >= 22:
            D = dist.Distortion(datadir.join('distortion_17.dist').strpath)
            assert abs(fmod.get_single_fiberflux(100, 200, D)
                       - 0.532356) < testprecision
            assert abs(fmod.get_single_fiberflux(1000, 1500, D)
                       - 0.59453) < testprecision
            assert abs(fmod.get_single_fiberflux(1000, 3000, D)
                       - 0.) < testprecision

    def test_single_fiberflux_fiber(self, datadir, fmod):
        if fmod.version >= 22:
            D = dist.Distortion(datadir.join('distortion_17.dist').strpath)
            assert abs(fmod.get_single_fiberflux_fiber(100, 200, 204, D)
                       - 0.53198) < testprecision
            assert abs(fmod.get_single_fiberflux_fiber(1000, 1500, 62, D)
                       - 0.59448) < testprecision
            assert abs(fmod.get_single_fiberflux_fiber(100, 200, 203, D)
                       - 0.00018) < testprecision
            assert abs(fmod.get_single_fiberflux_fiber(1000, 1500, 63, D)
                       - 0.00031) < testprecision
            assert abs(fmod.get_single_fiberflux_fiber(1000, 3000, 63, D)
                       - 0.0) < testprecision

    def test_single_fiberprofile(self, datadir, fmod):
        if fmod.version >= 22:
            D = dist.Distortion(datadir.join('distortion_17.dist').strpath)
            assert abs(fmod.get_single_fiberprofile(100, 200, D)
                       - 0.499776) < testprecision
            assert abs(fmod.get_single_fiberprofile(1000, 1500, D)
                       - 0.549257) < testprecision
            assert abs(fmod.get_single_fiberprofile(1000, 3000, D)
                       - 0.) < testprecision

    def test_single_fiberprofile_fiber(self, datadir, fmod):
        if fmod.version >= 22:
            D = dist.Distortion(datadir.join('distortion_17.dist').strpath)
            assert abs(fmod.get_single_fiberprofile_fiber(100, 200, 204, D)
                       - 0.499428) < testprecision
            assert abs(fmod.get_single_fiberprofile_fiber(1000, 1500, 62, D)
                       - 0.549209) < testprecision
            assert abs(fmod.get_single_fiberprofile_fiber(100, 200, 203, D)
                       - 0.000167601) < testprecision
            assert abs(fmod.get_single_fiberprofile_fiber(1000, 1500, 63, D)
                       - 0.000292374) < testprecision
            assert abs(fmod.get_single_fiberprofile_fiber(1000, 3000, 63, D)
                       - 0.0) < testprecision

    def test_cumulative_fiberflux(self, datadir, fmod):
        if fmod.version >= 22:
            D = dist.Distortion(datadir.join('distortion_17.dist').strpath)
            assert abs(fmod.get_cumulative_fiberflux(100, 200, D)
                       - 0.579471) < testprecision
            assert abs(fmod.get_cumulative_fiberflux(1000, 1500, D)
                       - 0.59504) < testprecision
            assert abs(fmod.get_cumulative_fiberflux(1000, 3000, D)
                       - 0.) < testprecision
