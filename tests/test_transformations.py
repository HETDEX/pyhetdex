"""Test the coordinate transformations in
pyhetdex.coordinates.transformations"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest

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
        assert hms == self.hms

    def test_dms2decimal2dms(self):
        "dms to decimal transformation and back"
        decimal = coo.dms2decimal(self.dms)
        dms = coo.decimal2dms(decimal)
        assert dms == self.dms

    # dms to decimal
    def test_dms2decimal(self):
        "dms to decimal transform"
        assert round(coo.dms2decimal(self.dms) - self.decimal, 8) == 0

    def test_dms2decimal_del(self):
        "dms to decimal transform (space delimiter)"
        dms = self.dms.replace(":", " ")
        assert round(coo.dms2decimal(dms, delimiter="") -
                     self.decimal, 8) == 0

    def test_dms2decimal_trunc(self):
        "dms to decimal transform (truncate to degrees)"
        dms = self.dms.split(":")[0]
        assert round(coo.dms2decimal(dms) - self.decimal_truncate_dms, 10) == 0

    def test_dms2decimal_neg(self):
        "dms to decimal transform (negative)"
        dms = self.dms.replace("+", "-")
        assert round(coo.dms2decimal(dms) + self.decimal, 8) == 0

    # decimal to dms
    def test_decimal2dms(self):
        "decimal to dms transform"
        assert coo.decimal2dms(self.decimal) == self.dms

    def test_decimal2dms_neg(self):
        "decimal to dms transform (negative)"
        dms = self.dms.replace("+", "-")
        assert coo.decimal2dms(-self.decimal) == dms

    # hms to decimal
    def test_hms2decimal(self):
        "hms to decimal transform"
        assert round(coo.hms2decimal(self.hms) - self.decimal, 5) == 0

    def test_hms2decimal_del(self):
        "hms to decimal transform (space delimiter)"
        hms = self.hms.replace(":", " ")
        assert round(coo.hms2decimal(hms, delimiter="") - self.decimal, 5) == 0

    @pytest.mark.todo
    def test_hms2decimal_trunc(self):
        "hms to decimal transform (truncate to degrees)"
        hms = self.hms.split(":")[0]
        assert round(coo.hms2decimal(hms) - self.decimal_truncate_hms, 10) == 0

    # decimal to hms
    def test_decimal2hms(self):
        "decimal to hms transform"
        assert coo.decimal2hms(self.decimal) == self.hms
