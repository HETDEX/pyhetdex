"""Test the angular coordinate distances in pyhetdex.coordinates.distances"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest

import pyhetdex.coordinates.distances as cdist


@pytest.mark.todo
def test_calcAngSepDeg():
    """Angular separation
    Reference separation from
    """
    ra1, dec1 = 31.4324, 68.5432
    ra2, dec2 = 45.65, 23.452
    # reference from http://cads.iiap.res.in/tools/angularSeparation
    ref_sep = 45.91686

    sep = cdist.angular_separation_deg(ra1, dec1, ra2, dec2)

    assert round(sep - ref_sep, 5) == 0

    ra1, dec1 = 100.2, -16.58
    ra2, dec2 = 87.5, 7.38
    # reference from http://cads.iiap.res.in/tools/angularSeparation
    ref_sep = 27.05438

    sep = cdist.angular_separation_deg(ra1, dec1, ra2, dec2)

    assert round(sep - ref_sep, 5) == 0
