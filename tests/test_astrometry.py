"""
Test the routines in the coordinates.astrometry module
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import pytest
import settings as s

from pyhetdex.coordinates.astrometry import add_ra_dec, add_wcs

fplane_file = os.path.join(s.datadir, "fplane.txt")
daophot_cat = os.path.join(s.datadir, "061706_074.als")
cont_cat = os.path.join(s.datadir, "detect046_cont.dat")
line_cat = os.path.join(s.datadir, "detect085_line.dat")
fits_image = os.path.join(s.datadir, "CuFepses20160604T063029.1_074_sci.fits")


@pytest.mark.parametrize("cat, typ, ihmp, regex", [
    (daophot_cat, "daophot_allstar", "074", None), 
    (daophot_cat, "daophot_allstar", None, "061706_(.*).als"),
    (cont_cat, "cont_detect", "046", None), 
    (cont_cat, "cont_detect", None, "detect(.*)_cont.dat"),
    (line_cat, "line_detect", "085", None), 
    (line_cat, "line_detect", None, "detect(.*)_line.dat"),
    ])
@pytest.mark.parametrize("outname", ['test.csv', 'test.fits'])
def test_add_ra_dec_cmd(cat, typ, ihmp, regex, outname, tmpdir): 
    """ 
    Test the add_ra_dec command runs for a variety of
    inputs
    """

    # create the arguments 
    out = tmpdir.join(outname).strpath
    print(out) 
    if ihmp:
        argv = ['--fplane', fplane_file, '--fout', out, '--ihmps', ihmp, 
                '--ftype', typ, '--astrometry', '205.543395821',  '28.3792133418', '257.654951', cat]
    else:
        argv = ['--fplane', fplane_file, '--fout', out, '--ihmp-regex', regex, 
                '--ftype', typ, '--astrometry', '205.543395821', '28.3792133418', '257.654951', cat]

    add_ra_dec(args=argv)
   
    # Check output file written
    assert os.path.isfile(out)
    

def test_add_wcs(tmpdir):
    """ Test the add_wcs command runs and outputs a file"""
    out = tmpdir.join("test.fits").strpath

    argv = ['--fplane', fplane_file, '--fout', out,
            '--astrometry', '205.543395821',  '28.3792133418', '257.654951', 
            fits_image, '074']

    add_wcs(args=argv)

    # Check output file written
    assert os.path.isfile(out)
 
      
