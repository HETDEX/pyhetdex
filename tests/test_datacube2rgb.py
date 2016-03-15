"""
tests for pyhetdex.tools.datacube2rgb
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import settings
import pytest

from pyhetdex.tools.datacube2rgb import main

datacube = os.path.join(settings.datadir, "Sigma_test_data.fits") 


def test_fluxes_and_snr_to_randoms_cmd(tmpdir):
    """test command line tool to add flux and snr to randoms"""
    test_im = str(tmpdir.join("TestIm.jpeg"))
    args = [datacube, test_im]
    main(args=args)

    assert os.path.exists(test_im), "could not create an image from a datacube"

