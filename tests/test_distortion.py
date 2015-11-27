"Test pyhetdex.cure.distortion"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pyhetdex.cure.distortion as distortion
import numpy as np
import pytest


@pytest.fixture(scope='module')
def dist(datadir):
    return distortion.Distortion(datadir.join('masterflat_001L.dist').strpath)


class TestDistortion(object):
    def test_dist_xf_y(self, dist):
        assert np.isclose(dist.map_xf_y([100, 1000], (20, 220)),
                          np.array([18.6529, 217.801])).all()

    def test_dist_xf_y_array(self, dist):
        assert np.isclose(dist.map_xf_y(np.array([100, 1000]),
                                        np.array([20, 220])),
                          np.array([18.6529, 217.801])).all()

    def test_dist_xy_fiber(self, dist):
        assert np.isclose(dist.map_xy_fiber([100, 1000], (200, 1500)),
                          np.array([201.066, 1498.73])).all()

    def test_dist_xy_fiber_array(self, dist):
        assert np.isclose(dist.map_xy_fiber(np.array([100, 1000]),
                                            np.array([200, 1500])),
                          np.array([201.066, 1498.73])).all()

    def test_dist_wf_y(self, dist):
        assert np.isclose(dist.map_wf_y([3600, 5000], (20, 220)),
                          np.array([17.8654, 220.41])).all()

    def test_dist_wf_y_array(self, dist):
        assert np.isclose(dist.map_wf_y(np.array([3600, 5000]),
                                        np.array([20, 220])),
                          np.array([17.8654, 220.41])).all()

    def test_maxf(self, dist):
        assert abs(dist.maxf - 2031.) < 1.e-4

    def test_version(self, dist):
        assert dist.version == 14

    def test_wrong_version(self, datadir):
        with pytest.raises(IOError):
            distortion.Distortion(datadir.join('masterflat_001L_old.dist').strpath)

    def test_cheb(self, dist):
        import pyhetdex.ltl.marray as ma
        x = (dist._scal_x(100), dist._scal_x(1000))
        y = [dist._scal_f(20), dist._scal_f(220)]
        assert np.isclose(ma.interpCheby2D_7(x, y, dist.fy_par_.data),
                          np.array([18.6529, 217.801])).all()
