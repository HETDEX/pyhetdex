"Test pyhetdex.ltl.marray"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

import pytest

import pyhetdex.ltl.marray as ma


@pytest.mark.parametrize('obj, typ, value',
                         (['fvec', 'int', [1, 2, 3]],
                          ['fvec', 'float', [1.23, 2.34, 3.45]],
                          ['fvec', 'double', [10.234, 20.345, 30.456]],
                          ['marray', 'int', [[11, 21, 31], [12, 22, 32],
                                             [13, 23, 33]]],
                          ['marray', 'float', [[11.123, 21.123, 31.123],
                                               [12.123, 22.123, 32.123],
                                               [13.123, 23.123, 33.123]]],
                          ['marray', 'double', [[21.123, 41.123, 61.123],
                                                [22.123, 42.123, 62.123],
                                                [23.123, 43.123, 63.123]]]))
@pytest.mark.parametrize('test', ['r', 'rw'])
def test_readwrite(datadir, tmpdir, obj, typ, value, test):

    dtypemap = {'int': 'int', 'float': 'float32', 'double': 'float64'}
    precmap = {'int': 1.e-10, 'float': 1.e-4, 'double': 1.e-10}
    reffilename = datadir.join("test"+obj+"_"+typ+".dat")

    if 'w' in test:
        if obj == 'fvec':
            outvec = ma.FVector()
        else:
            outvec = ma.MArray()
        outvec.data = np.array(value, dtype=dtypemap[typ])
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
            if obj == 'fvec':
                invec = ma.FVector(outfilename.strpath)
            else:
                invec = ma.MArray(outfilename.strpath)
        else:
            if obj == 'fvec':
                invec = ma.FVector()
            else:
                invec = ma.MArray()
            invec.read(infilename.open())

    if test == 'r':
        expected = np.array(value, dtype=dtypemap[typ])
        actual = invec.data
    elif test == 'rw':
        expected = invec.data
        actual = outvec.data

    assert np.isclose(expected, actual, precmap[typ]).all()


@pytest.mark.parametrize('obj', ['fvec', 'marray'])
def test_exceptions(datadir, obj):

    if obj == 'fvec':
        t = ma.FVector()
    else:
        t = ma.MArray()

    with pytest.raises(TypeError):
        t.data = 2

    if obj == 'fvec':
        with pytest.raises(TypeError):
            t.data = np.array([[1, 2], [1, 2]])

    with pytest.raises(TypeError):
        t.data = np.array([1, 2], dtype=bool)

    if obj == 'fvec':
        with pytest.raises(TypeError):
            t.read(datadir.join("testmarray_int.dat").open())
    else:
        with pytest.raises(TypeError):
            t.read(datadir.join("testfvec_int.dat").open())

    if obj == 'fvec':
        with pytest.raises(TypeError):
            t.read(datadir.join("testfvec_char.dat").open())
    else:
        with pytest.raises(TypeError):
            t.read(datadir.join("testmarray_char.dat").open())
