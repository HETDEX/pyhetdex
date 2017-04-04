"""Test pyhetdex.tools.create_mask"""
from __future__ import (absolute_import, print_function)

import os.path
import pytest

from pyhetdex.tools.create_mask import generate_mangle_polyfile

def test_generate_mangle_polyfile(tmpdir, fplane_file):
    """
    Test that the tool produces an output file
    """
 
    # create an input file
    infile = tmpdir.join('input.txt')

    with open(infile.strpath, 'w') as fp:
        fp.write("# SHOTID    RACEN          DECCEN       PARANGLE    FPLANE\n")
        fp.write("M3_0001   205.547        28.376        254.6   {:s}\n".format(fplane_file.strpath)) 
        fp.write("virus0234 181.264005    53.724400     63.745977 {:s}\n".format(fplane_file.strpath))
 
    # run command
    outfile = tmpdir.join('output.ver')
    args = [infile.strpath, outfile.strpath, '1.8']
    generate_mangle_polyfile(args=args)
   
    # check output produced
    assert os.path.isfile(outfile.strpath)   

 


    




