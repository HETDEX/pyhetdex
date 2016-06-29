"Test pyhetdex.cure.fibermodel"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pyhetdex.cure.psfmodel as psfm
import pytest
import locale


@pytest.fixture(scope='module', params=['psfmodel_2.pmod',
                                        'psfmodel_3.pmod'])
def pmod(datadir, request):
    return psfm.PSFModel(datadir.join(request.param).strpath)


class TestPSFModel(object):
    def test_version(self, pmod):
        expected = pmod.filename.split('.')[-2].split('_')[-1]
        assert pmod.version == locale.atoi(expected)

    def test_maxx(self, pmod):
        if pmod.version == 2:
            assert pmod.maxx == 1031
        else:
            assert pmod.maxx == 1033

    def test_wrong_version(self, datadir):
        with pytest.raises(Exception):
            psfm.PSFModel(datadir.join('psfmodel_1.pmod').strpath)
