"Test pyhetdex.cure.distortion"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pyhetdex.cure.distortion as distortion
import numpy as np
import pytest
import subprocess


__version__ = '$Id'


@pytest.fixture(scope='module', params=['distortion_14.dist',
                                        'distortion_17.dist'])
def dist(datadir, request):
    'return a distortion object'
    return distortion.Distortion(datadir.join(request.param).strpath)


class TestDistortion(object):
    def test_dist_xf_y(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_xf_y([100, 1000], (20, 220)),
                              np.array([18.6529, 217.801])).all()
        else:
            assert np.isclose(dist.map_xf_y([100, 1000], (20, 220)),
                              np.array([14.9945, 212.873])).all()

    def test_dist_xf_y_array(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_xf_y(np.array([100, 1000]),
                                            np.array([20, 220])),
                              np.array([18.6529, 217.801])).all()
        else:
            assert np.isclose(dist.map_xf_y(np.array([100, 1000]),
                                            np.array([20, 220])),
                              np.array([14.9945, 212.873])).all()

    def test_dist_xy_fiber(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_xy_fiber([100, 1000], (200, 1500)),
                              np.array([201.066, 1498.73])).all()
        else:
            assert np.isclose(dist.map_xy_fiber([100, 1000], (200, 1500)),
                              np.array([204.086, 1495.69])).all()

    def test_dist_xy_wf(self, dist):
        # OCD Test...
        if dist.version == 14:
            w, f = dist.map_xy_wf(100, 200)
            assert np.isclose(w, 3696.6) and np.isclose(f, 201.066)
        else:
            w, f = dist.map_xy_wf(100, 200)
            assert np.isclose(w, 3685.32) and np.isclose(f, 204.086)

    def test_dist_xy_fiber_array(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_xy_fiber(np.array([100, 1000]),
                                                np.array([200, 1500])),
                              np.array([201.066, 1498.73])).all()
        else:
            assert np.isclose(dist.map_xy_fiber(np.array([100, 1000]),
                                                np.array([200, 1500])),
                              np.array([204.086, 1495.69])).all()

    def test_dist_xy_fibernum(self, dist):
        if dist.version == 14:
            assert (dist.map_xy_fibernum([100, 1000], (200, 1500)) ==
                    np.array([203, 62])).all()
        else:
            assert (dist.map_xy_fibernum([100, 1000], (200, 1500)) ==
                    np.array([204, 62])).all()

    def test_dist_xy_wavelength(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_xy_wavelength([100, 1000], (200, 1500)),
                              np.array([3696.6, 5434.6])).all()
        else:
            assert np.isclose(dist.map_xy_wavelength([100, 1000], (200, 1500)),
                              np.array([3685.32, 5468.21])).all()

    def test_dist_xy_wavelength_array(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_xy_wavelength(np.array([100, 1000]),
                                                     np.array([200, 1500])),
                              np.array([3696.6, 5434.6])).all()
        else:
            assert np.isclose(dist.map_xy_wavelength(np.array([100, 1000]),
                                                     np.array([200, 1500])),
                              np.array([3685.32, 5468.21])).all()

    def test_dist_wf_x(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_wf_x([3600, 5000], (20, 220)),
                              np.array([52.9629, 778.098])).all()
            assert np.isclose(dist.map_wf_x(3600, 20), 52.9629)
        else:
            assert np.isclose(dist.map_wf_x([3600, 5000], (20, 220)),
                              np.array([57.713, 763.913])).all()
            assert np.isclose(dist.map_wf_x(3600, 20), 57.713)

    def test_dist_wf_x_array(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_wf_x(np.array([3600, 5000]),
                                            np.array([20, 220])),
                              np.array([52.9629, 778.098])).all()
        else:
            assert np.isclose(dist.map_wf_x(np.array([3600, 5000]),
                                            np.array([20, 220])),
                              np.array([57.713, 763.913])).all()

    def test_dist_wf_y(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_wf_y([3600, 5000], (20, 220)),
                              np.array([17.8654, 220.41])).all()
        else:
            assert np.isclose(dist.map_wf_y([3600, 5000], (20, 220)),
                              np.array([13.5371, 218.609])).all()

    def test_dist_wf_y_array(self, dist):
        if dist.version == 14:
            assert np.isclose(dist.map_wf_y(np.array([3600, 5000]),
                                            np.array([20, 220])),
                              np.array([17.8654, 220.41])).all()
        else:
            assert np.isclose(dist.map_wf_y(np.array([3600, 5000]),
                                            np.array([20, 220])),
                              np.array([13.5371, 218.609])).all()

    def test_maxf(self, dist):
        if dist.version == 14:
            assert abs(dist.maxf - 2031.) < 1.e-4
        else:
            assert abs(dist.maxf - 2065.) < 1.e-4

    def test_numfibers(self, dist):
        assert dist.get_numfibers() == 224

    def test_reference_f(self, dist):
        if dist.version == 14:
            assert abs(dist.get_reference_f(1)-2054.9929) < 1e4
        else:
            assert abs(dist.get_reference_f(1)-2045.011) < 1e4

    def test_version(self, dist):
        expected = dist.filename.split('.')[-2].split('_')[-1]
        assert dist.version == int(expected)

    def test_wrong_version(self, datadir):
        with pytest.raises(IOError):
            distortion.Distortion(datadir.join('distortion_12.dist').strpath)

    def test_write(self, dist, tmpdir):
        if dist.version >= 14:
            dname = tmpdir.strpath + '/test.dist'
            dist.writeto(dname)
            D = distortion.Distortion(dname)
            assert dist.version == D.version
            assert np.isclose(dist.maxx, D.maxx)
            assert np.isclose(dist.wave_par_.data,
                              D.wave_par_.data).all()
            assert np.isclose(dist.reference_w_.data,
                              D.reference_w_.data).all()
            assert np.isclose(dist.reference_wavelength_,
                              D.reference_wavelength_)

    def test_write_ltl(self, dist, tmpdir, skip_if_no_executable):
        curever = skip_if_no_executable('cureversion')
        versions = subprocess.check_output(curever,
                                           universal_newlines=True).strip()
        for k, v in [ver.split() for ver in versions.split('\n')]:
            if k == 'Distortion':
                distver = int(v)
                break
        if dist.version == distver:  # Skip till distview is fixed
            exe = skip_if_no_executable('distview')
            dname = tmpdir.strpath + '/test2.dist'
            dist.writeto(dname)
            orig = subprocess.check_output([exe, dist.filename],
                                           universal_newlines=True)
            mine = subprocess.check_output([exe, dname],
                                           universal_newlines=True)

            assert orig == mine
        else:
            pytest.skip()

    def test_cheb(self, dist):
        import pyhetdex.ltl.marray as ma
        x = (dist._scal_x(100), dist._scal_x(1000))
        y = [dist._scal_f(20), dist._scal_f(220)]
        if dist.version == 14:
            assert np.isclose(ma.interpCheby2D_7(x, y, dist.fy_par_.data),
                              np.array([18.6529, 217.801])).all()
        else:
            assert np.isclose(ma.interpCheby2D_7(x, y, dist.fy_par_.data),
                              np.array([14.9945, 212.873])).all()
