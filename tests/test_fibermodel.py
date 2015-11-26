"Test pyhetdex.cure.fibermodel"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pyhetdex.cure.fibermodel as fib
import pytest


def test_distortion(datadir):

    F = fib.FiberModel(datadir.join('masterflat_081_L.fmod').strpath)

    assert F.version == 16

    assert F.fiducial_fib_ == 110

    assert len(F.amplitudes) == 224

    with pytest.raises(Exception):
        F = fib.FiberModel(datadir.join('masterflat_081_L_old.fmod').strpath)
