"""Test the coordinate transformations in pyhetdex.common.coords"""

import nose.tools as nt

import pyhetdex.coordinates.transformations as coo


class TestCoordTransform(object):
    "Test the coordinate transformation"

    @classmethod
    def setup_class(cls):
        """Values to convert and to check against. Computed using
        https://ned.ipac.caltech.edu/forms/calculator.html
        """
        cls.hms = "02:41:43.033"
        cls.dms = "+40:25:45.50"
        cls.decimal = 40.42930556
        # truncate the dms and hms to the first element
        cls.decimal_truncate_dms = 40.
        cls.decimal_truncate_hms = 30.

        return cls

    # direct and inverse transform
    def test_hms2decimal2hms(self):
        "hms to decimal transformation and back"
        decimal = coo.hms2decimal(self.hms)
        hms = coo.decimal2hms(decimal)
        nt.assert_equal(hms, self.hms)

    def test_dms2decimal2dms(self):
        "dms to decimal transformation and back"
        decimal = coo.dms2decimal(self.dms)
        dms = coo.decimal2dms(decimal)
        nt.assert_equal(dms, self.dms)

    # dms to decimal
    def test_dms2decimal(self):
        "dms to decimal transform"
        nt.assert_almost_equal(coo.dms2decimal(self.dms), self.decimal)

    def test_dms2decimal_del(self):
        "dms to decimal transform (space delimiter)"
        dms = self.dms.replace(":", " ")
        nt.assert_almost_equal(coo.dms2decimal(dms, delimiter=""),
                               self.decimal)

    def test_dms2decimal_trunc(self):
        "dms to decimal transform (truncate to degrees)"
        dms = self.dms.split(":")[0]
        nt.assert_almost_equal(coo.dms2decimal(dms),
                               self.decimal_truncate_dms)

    def test_dms2decimal_neg(self):
        "dms to decimal transform (negative)"
        dms = self.dms.replace("+", "-")
        nt.assert_almost_equal(coo.dms2decimal(dms), -self.decimal)

    # decimal to dms
    def test_decimal2dms(self):
        "decimal to dms transform"
        nt.assert_almost_equal(coo.decimal2dms(self.decimal), self.dms)

    def test_decimal2dms_neg(self):
        "decimal to dms transform (negative)"
        dms = self.dms.replace("+", "-")
        nt.assert_almost_equal(coo.decimal2dms(-self.decimal), dms)

    # hms to decimal
    def test_hms2decimal(self):
        "hms to decimal transform"
        nt.assert_almost_equal(coo.hms2decimal(self.hms), self.decimal,
                               delta=1e-5)

    def test_hms2decimal_del(self):
        "hms to decimal transform (space delimiter)"
        hms = self.hms.replace(":", " ")
        nt.assert_almost_equal(coo.hms2decimal(hms, delimiter=""),
                               self.decimal, delta=1e-5)

    def test_hms2decimal_trunc(self):
        "hms to decimal transform (truncate to degrees)"
        hms = self.hms.split(":")[0]
        nt.assert_almost_equal(coo.hms2decimal(hms),
                               self.decimal_truncate_hms)

    # decimal to hms
    def test_decimal2hms(self):
        "decimal to hms transform"
        nt.assert_almost_equal(coo.decimal2hms(self.decimal), self.hms)


def test_calcAngSepDeg():
    """Angular separation
    Reference separation from
    """
    ra1, dec1 = 31.4324, 68.5432
    ra2, dec2 = 45.65, 23.452
    ref_sep = 0.

    sep = coo.calcAngSepDeg(ra1, dec1, ra2, dec2)

    nt.assert_almost_equal(sep, ref_sep)
