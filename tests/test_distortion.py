"Test pyhetdex.cure.distortion"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pyhetdex.cure.distortion as dist
import numpy as np
import pytest


def test_distortion(datadir):

    D = dist.Distortion(datadir.join('masterflat_001L.dist').strpath)

    assert np.isclose(D.map_xf_y([100, 1000], (20, 220)),
                      np.array([18.6529, 217.801]), 8).all()

    assert np.isclose(D.map_xf_y(np.array([100, 1000]), (20, 220)),
                      np.array([18.6529, 217.801]), 8).all()

    assert np.isclose(D.map_xf_y(np.array([100, 1000]), np.array([20, 220])),
                      np.array([18.6529, 217.801]), 8).all()

    assert abs(D.maxf - 2031.) < 1.e-4

    assert D.version == 14

    with pytest.raises(Exception):
        D = dist.Distortion(datadir.join('masterflat_001L_old.dist').strpath)
