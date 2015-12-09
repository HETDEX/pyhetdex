"Test pyhetdex.cure.fibermodel"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pyhetdex.cure.psfmodel as psfm
import pytest


@pytest.fixture(scope='module')
def pmod(datadir):
    return psfm.PSFModel(datadir.join('masterflat_081_L.pmod').strpath)


class TestPSFModel(object):
    def test_version(self, pmod):
        assert pmod.version == 2

    def test_maxx(self, pmod):
        assert pmod.maxx == 1031

    def test_wrong_version(self, datadir):
        with pytest.raises(Exception):
            psfm.PSFModel(datadir.join('masterflat_081_L_old.pmod').strpath)
