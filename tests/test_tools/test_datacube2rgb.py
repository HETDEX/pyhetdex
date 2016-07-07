"""
tests for pyhetdex.tools.datacube2rgb
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest

from pyhetdex.tools.datacube2rgb import main


@pytest.fixture
def datacube(datadir):
    'returns the reference data cube as a py.path.local object'
    return datadir.join("Sigma_test_data.fits")


def test_fluxes_and_snr_to_randoms_cmd(tmpdir, datacube):
    """test command line tool to add flux and snr to randoms"""
    test_im = tmpdir.join("TestIm.jpeg")
    args = [datacube.strpath, test_im.strpath]
    main(args=args)

    assert test_im.check(file=True), "no image created from a datacube"
