"""
Test the routines in the coordinates.astrometry module
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import pytest

from pyhetdex.coordinates.astrometry import add_ra_dec, add_wcs


@pytest.fixture
def daophot_cat(datadir):
    '''Return the daophot file as a py.path.local instance'''
    return datadir.join("061706_074.als")


@pytest.fixture
def fits_image(datadir):
    '''Returns a datacube as a py.path.local instance'''
    return datadir.join("CuFepses20160604T063029.1_074_sci.fits")


@pytest.mark.parametrize("cat, typ, ihmp, regex", [
    ('daophot_cat', "daophot_allstar", "074", None),
    ('daophot_cat', "daophot_allstar", None, "061706_(.*).als"),
    ('cont_detection', "cont_detect", "046", None),
    ('cont_detection', "cont_detect", None, "detect(.*)_cont.dat"),
    ('line_detection', "line_detect", "085", None),
    ('line_detection', "line_detect", None, "detect(.*)_line.dat"),
    ])
@pytest.mark.parametrize("outname", ['test.csv', 'test.fits', 'test.txt'])
def test_add_ra_dec_cmd(tmpdir, request, fplane_file, cat, typ, ihmp, regex,
                        outname):
    """Test the add_ra_dec command runs for a variety of inputs """
    # create the arguments
    cat = request.getfuncargvalue(cat).strpath
    out = tmpdir.join(outname).strpath

    argv = ['--fplane', fplane_file.strpath, '--fout', out]
    if ihmp:
        argv += ['--ihmps', ihmp]
    else:
        argv += ['--ihmp-regex', regex]

    argv += ['--ftype', typ, '--astrometry', '205.543395821', '28.3792133418',
             '257.654951', cat]

    add_ra_dec(args=argv)
    # Check output file written
    assert os.path.isfile(out)


def test_add_wcs(tmpdir, fplane_file, fits_image):
    """ Test the add_wcs command runs and outputs a file"""
    out = tmpdir.join("test.fits").strpath

    argv = ['--fplane', fplane_file.strpath, '--fout', out, '--astrometry',
            '205.543395821',  '28.3792133418', '257.654951',
            fits_image.strpath, '074']

    add_wcs(args=argv)

    # Check output file written
    assert os.path.isfile(out)
