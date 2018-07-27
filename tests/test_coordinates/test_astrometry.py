"""
Test the routines in the coordinates.astrometry module
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import pytest

from pyhetdex.coordinates.astrometry import (add_ra_dec, add_wcs, xy_to_ra_dec,
                                             add_ifu_xy)

@pytest.fixture
def ifucen_file_missf(datadir):
    '''Return an ifu cen file as a py.path.local instance'''
    return datadir.join("IFUcen_HETDEX_missf.txt")

@pytest.fixture
def ifucen_file(datadir):
    '''Return an ifu cen file as a py.path.local instance'''
    return datadir.join("IFUcen_HETDEX.txt")


@pytest.fixture
def daophot_cat(datadir):
    '''Return the daophot file as a py.path.local instance'''
    return datadir.join("061706_074.als")


@pytest.fixture
def ra_dec_cat_csv(datadir):
    '''Return a file with ra, dec as a py.path.local instance'''
    return datadir.join("061706_074_ra_dec.csv")


@pytest.fixture
def ra_dec_cat_fits(datadir):
    '''Return a fits file with ra, dec as a py.path.local instance'''
    return datadir.join("061706_074_ra_dec.fits")


@pytest.fixture
def fits_image(datadir):
    '''Returns a datacube as a py.path.local instance'''
    return datadir.join("CuFepses20160604T063029.1_074_sci.fits")


@pytest.mark.parametrize("cat, typ, ihmp, regex", [
    ("ifucen_file", "ifucen", "074", None),
    ("ifucen_file_missf", "ifucen", "074", None),
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
    cat = request.getfixturevalue(cat).strpath
    out = tmpdir.join(outname).strpath

    argv = ['--fplane', fplane_file.strpath, '--fout', out]
    if ihmp:
        argv += ['--ihmps', ihmp]
    else:
        argv += ['--ihmp-regex', regex]

    argv += ['--ftype', typ, '--astrometry', '205.543395821', '28.3792133418',
             '257.654951', cat]

    print(argv)

    add_ra_dec(args=argv)
    # Check output file written
    assert os.path.isfile(out)


@pytest.mark.parametrize("cat", ['ra_dec_cat_csv', 'ra_dec_cat_fits'])
@pytest.mark.parametrize("outname", ['test.csv', 'test.fits'])
def test_add_ifu_xy_cmd(tmpdir, request, fplane_file, cat, outname):

    """ Test adding x, y to a catalogue. Use output from test_ra_dec_cmd """
    cat_fn = request.getfixturevalue(cat).strpath
    out = tmpdir.join(outname).strpath

    argv = ['--fplane', fplane_file.strpath]
    argv += ['--astrometry', '205.543395821', '28.3792133418',
             '257.654951', cat_fn, out]

    add_ifu_xy(args=argv)

    # Check output file written
    assert os.path.isfile(out)


@pytest.mark.parametrize("rhozp_toggle", [True, False])
def test_xy_to_ra_dec_cmd(capsys, fplane_file, rhozp_toggle):
    """Test the add_ra_dec command runs for a variety of inputs """

    # create the arguments
    argv = ['--fplane', fplane_file.strpath]
    argv += ['--ihmp', '073']

    if rhozp_toggle:
        argv += ['--rhozp', '1.3']

    argv += ['--astrometry', '205.547', '28.376', '254.6']
    argv += ['20.969', '-23.712']

    xy_to_ra_dec(args=argv)

    out, err = capsys.readouterr()

    # Check output file written (values for old fplane)
    if rhozp_toggle:
        assert out.strip().split()[0] == '205.484923'
        assert out.strip().split()[1] == '28.398439'
    else:
        assert out.strip().split()[0] == '205.484361'
        assert out.strip().split()[1] == '28.397195'


def test_add_wcs(tmpdir, clear_tmpdir, fplane_file, fits_image):
    """ Test the add_wcs command runs and outputs a file"""
    out = tmpdir.join("test.fits").strpath

    argv = ['--fplane', fplane_file.strpath, '--fout', out, '--astrometry',
            '205.543395821',  '28.3792133418', '257.654951',
            fits_image.strpath, '074']

    add_wcs(args=argv)

    # Check output file written
    assert os.path.isfile(out)
