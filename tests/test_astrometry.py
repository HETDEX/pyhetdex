"""
Test pyhetdex/astrometry/astrometry.py
"""
from __future__ import print_function, absolute_import

import nose.tools as nt

import pyhetdex.astrometry.astrometry as am


class TestAstrometry(object):
    """
    class to test the astrometry
    """

    def setUp(self):
        ra0 = 0.
        dec0 = 70.
        rot = 0.
        self.x_in, self.y_in = 10., 0.
        self.ra_in, self.dec_in = 60, 0.
        self.ifuastrom = am.IFUAstrom(ra0=ra0, dec0=dec0, rot=rot, x_scale=-1,
                                      y_scale=1)

    def test_tan_dir(self):
        "Test the direct transform"
        x, y = am.tan_dir(self.ifuastrom, self.ra_in, self.dec_in)
        exp_x, exp_y = -1044561.64704, -566707.897592
        nt.assert_almost_equal(exp_x, x, delta=1e-5)
        nt.assert_almost_equal(exp_y, y, delta=1e-5)

    def test_tan_inv(self):
        "Test the inverse transform"
        ra, dec = am.tan_inv(self.ifuastrom, self.x_in, self.y_in)
        exp_ra, exp_dec = -0.00812167883495, 69.999999815
        nt.assert_almost_equal(exp_ra, ra)
        nt.assert_almost_equal(exp_dec, dec)


    def test_tan_dirinv(self):
        """Test chaining the direct and inverse transform"""
        x, y = am.tan_dir(self.ifuastrom, self.ra_in, self.dec_in)
        ra, dec = am.tan_inv(self.ifuastrom, x, y)
        nt.assert_almost_equal(self.ra_in, ra)
        nt.assert_almost_equal(self.dec_in, dec)

    def test_tan_invdir(self):
        """Test chaining the inverse and direct transform"""
        ra, dec = am.tan_inv(self.ifuastrom, self.x_in, self.y_in)
        x, y = am.tan_dir(self.ifuastrom, ra, dec)
        nt.assert_almost_equal(self.x_in, x)
        nt.assert_almost_equal(self.y_in, y)
