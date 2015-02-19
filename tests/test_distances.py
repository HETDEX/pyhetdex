"""Test the angular coordinate distances in pyhetdex.coordinates.distances"""

import nose.tools as nt

import pyhetdex.coordinates.distances as cdist


def test_calcAngSepDeg():
    """Angular separation
    Reference separation from
    """
    ra1, dec1 = 31.4324, 68.5432
    ra2, dec2 = 45.65, 23.452
    ref_sep = 0.

    sep = cdist.angular_separation_deg(ra1, dec1, ra2, dec2)

    nt.assert_almost_equal(sep, ref_sep)
