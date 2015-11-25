"Test pyhetdex.cure.marray"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

import pytest
import conftest

import pyhetdex.ltl.marray as ma


@pytest.mark.parametrize('obj, typ, value',
                         (['fvec', 'int', [1, 2, 3]],
                          ['fvec', 'float', [1.23, 2.34, 3.45]],
                          ['marray', 'int', [[11, 12, 13], [21, 22, 23],
                                             [31, 32, 33]]],
                          ['marray', 'float', [[11.123, 12.123, 13.123],
                                               [21.123, 22.123, 23.123],
                                               [31.123, 32.123, 33.123]]]))
@pytest.mark.parametrize('test', ['r', 'rw'])
def test_fvector(datadir, tmpdir, obj, typ, value, test):

    reffilename = datadir.join("test"+obj+"_"+typ+".dat")

    if 'w' in test:
        if obj == 'fvec':
            outvec = ma.FVector()
        else:
            outvec = ma.MArray()
        outvec.data = np.array(value)
        if type(obj) == ma.FVector:
            outfilename = tmpdir.mkdir('marray').join('test_fvec.dat')
        else:
            outfilename = tmpdir.mkdir('marray').join('test_marray.dat')
        outfile = outfilename.open('w')
        outvec.write(outfile)
        outfile.close()

    if 'r' in test:
        infilename = reffilename
        if test == 'rw':  # Reread file
            infilename = outfilename
        if obj == 'fvec':
            invec = ma.FVector()
        else:
            invec = ma.MArray()
        invec.read(infilename.open())

    if test == 'r':
        expected = np.array(value)
        actual = invec.data
    elif test == 'rw':
        expected = invec.data
        actual = outvec.data

    np.isclose(expected, actual, 1.e-10)
