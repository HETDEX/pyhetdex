"Test pyhetdex.cure.distortion"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__version__ = '$Id'

import pyhetdex.cure.distortion as distortion
import numpy as np
import pytest
import locale


@pytest.fixture(scope='module', params=['distortion_14.dist',
                                        'distortion_17.dist'])
def dist(datadir, request):
    return distortion.Distortion(datadir.join(request.param).strpath)


class TestDistortion(object):
    def test_dist_xf_y(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_xf_y([100, 1000], (20, 220)),
                              np.array([18.6529, 217.801])).all()
        else:
            assert np.isclose(dist.map_xf_y([100, 1000], (20, 220)),
                              np.array([20.9811, 211.596])).all()

    def test_dist_xf_y_array(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_xf_y(np.array([100, 1000]),
                                            np.array([20, 220])),
                              np.array([18.6529, 217.801])).all()
        else:
            assert np.isclose(dist.map_xf_y(np.array([100, 1000]),
                                            np.array([20, 220])),
                              np.array([20.9811, 211.596])).all()

    def test_dist_xy_fiber(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_xy_fiber([100, 1000], (200, 1500)),
                              np.array([201.066, 1498.73])).all()
        else:
            assert np.isclose(dist.map_xy_fiber([100, 1000], (200, 1500)),
                              np.array([199.062, 1496.21])).all()

    def test_dist_xy_wf(self, dist):
        # OCD Test...
        if dist.version == 14:
            w, f = dist.map_xy_wf(100, 200)
            assert np.isclose(w, 3696.6) and np.isclose(f, 201.066)
        else:
            w, f = dist.map_xy_wf(100, 200)
            assert np.isclose(w, 3674.79) and np.isclose(f, 199.062)

    def test_dist_xy_fiber_array(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_xy_fiber(np.array([100, 1000]),
                                                np.array([200, 1500])),
                              np.array([201.066, 1498.73])).all()
        else:
            assert np.isclose(dist.map_xy_fiber(np.array([100, 1000]),
                                                np.array([200, 1500])),
                              np.array([199.062, 1496.21])).all()

    def test_dist_xy_fibernum(self, dist):
        if dist.version == 14:
            assert (dist.map_xy_fibernum([100, 1000], (200, 1500))
                    == np.array([203, 62])).all()
        else:
            assert (dist.map_xy_fibernum([100, 1000], (200, 1500))
                    == np.array([203, 62])).all()

    def test_dist_xy_wavelength(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_xy_wavelength([100, 1000], (200, 1500)),
                              np.array([3696.6, 5434.6])).all()
        else:
            assert np.isclose(dist.map_xy_wavelength([100, 1000], (200, 1500)),
                              np.array([3674.79, 5464.62])).all()

    def test_dist_xy_wavelength_array(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_xy_wavelength(np.array([100, 1000]),
                                                     np.array([200, 1500])),
                              np.array([3696.6, 5434.6])).all()
        else:
            assert np.isclose(dist.map_xy_wavelength(np.array([100, 1000]),
                                                     np.array([200, 1500])),
                              np.array([3674.79, 5464.62])).all()

    def test_dist_wf_x(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_wf_x([3600, 5000], (20, 220)),
                              np.array([52.9629, 778.098])).all()
            assert np.isclose(dist.map_wf_x(3600, 20), 52.9629)
        else:
            assert np.isclose(dist.map_wf_x([3600, 5000], (20, 220)),
                              np.array([62.3172, 766.703])).all()
            assert np.isclose(dist.map_wf_x(3600, 20), 62.3172)

    def test_dist_wf_x_array(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_wf_x(np.array([3600, 5000]),
                                            np.array([20, 220])),
                              np.array([52.9629, 778.098])).all()
        else:
            assert np.isclose(dist.map_wf_x(np.array([3600, 5000]),
                                            np.array([20, 220])),
                              np.array([62.3172, 766.703])).all()

    def test_dist_wf_y(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_wf_y([3600, 5000], (20, 220)),
                              np.array([17.8654, 220.41])).all()
        else:
            assert np.isclose(dist.map_wf_y([3600, 5000], (20, 220)),
                              np.array([20.1775, 218.321])).all()

    def test_dist_wf_y_array(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_wf_y(np.array([3600, 5000]),
                                            np.array([20, 220])),
                              np.array([17.8654, 220.41])).all()
        else:
            assert np.isclose(dist.map_wf_y(np.array([3600, 5000]),
                                            np.array([20, 220])),
                              np.array([20.1775, 218.321])).all()

    def test_maxf(self, dist):
        assert abs(dist.maxf - 2031.) < 1.e-4

    def test_version(self, dist):
        expected = dist.filename.split('.')[-2].split('_')[-1]
        assert dist.version == locale.atoi(expected)

    def test_wrong_version(self, datadir):
        with pytest.raises(IOError):
            distortion.Distortion(datadir.join('distortion_12.dist').strpath)

    def test_cheb(self, dist):
        import pyhetdex.ltl.marray as ma
        x = (dist._scal_x(100), dist._scal_x(1000))
        y = [dist._scal_f(20), dist._scal_f(220)]
        if dist.version == 14:
            assert np.isclose(ma.interpCheby2D_7(x, y, dist.fy_par_.data),
                              np.array([18.6529, 217.801])).all()
        else:
            assert np.isclose(ma.interpCheby2D_7(x, y, dist.fy_par_.data),
                              np.array([20.9811, 211.596])).all()
