"Test pyhetdex.cure.fibermodel"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pyhetdex.cure.fibermodel as fib
import pytest


@pytest.fixture(scope='module')
def fmod(datadir):
    return fib.FiberModel(datadir.join('masterflat_081_L.fmod').strpath)


class TestFibermdoel(object):
    def test_version(self, fmod):
        assert fmod.version == 16

    def test_fiducial(self, fmod):
        assert fmod.fiducial_fib_ == 110

    def test_ampsize(self, fmod):
        assert len(fmod.amplitudes) == 224

    def test_wrong_version(self, datadir):
        with pytest.raises(Exception):
            fib.FiberModel(datadir.join('masterflat_081_L_old.fmod').strpath)
