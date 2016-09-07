"Test pyhetdex.ltl.marray"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pytest

import pyhetdex.ltl.marray as ma

dtypemap = {'int': 'int', 'float': 'float32', 'double': 'float64'}
# precmap = {'int': 10, 'float': 1.e-4, 'double': 1.e-10}
clsmap = {'fvec': ma.FVector, 'marray': ma.MArray}


def pytest_generate_tests(metafunc):
    # called once per each test function
    if metafunc.cls:
        funcarglist = metafunc.cls.params[metafunc.function.__name__]
        argnames = list(funcarglist[0])
        metafunc.parametrize(argnames, [[funcargs[name] for name in argnames]
                                        for funcargs in funcarglist])


def write(outname, cls_type, typ, data):
    out = clsmap[cls_type]()
    out.data = np.array(data, dtype=dtypemap[typ])
    outfile = outname.open('w')
    out.write(outfile)
    outfile.close()


def read(cls_type, fname):
    return clsmap[cls_type](fname)


class TestFVectorMArray(object):

    full_fvec_params = [dict(cls_type='fvec', typ='int', data=[1, 2, 3]),
                        dict(cls_type='fvec', typ='float',
                             data=[1.23, 2.34, 3.45]),
                        dict(cls_type='fvec', typ='double',
                             data=[10.234, 20.345, 30.456]),
                        dict(cls_type='marray', typ='int',
                             data=[[11, 21, 31], [12, 22, 32],
                                   [13, 23, 33]]),
                        dict(cls_type='marray', typ='float',
                             data=[[11.123, 21.123, 31.123],
                                   [12.123, 22.123, 32.123],
                                   [13.123, 23.123, 33.123]]),
                        dict(cls_type='marray', typ='double',
                             data=[[21.123, 41.123, 61.123],
                                   [22.123, 42.123, 62.123],
                                   [23.123, 43.123, 63.123]])]
    only_class_params = [dict(cls_type='fvec'), dict(cls_type='marray')]
    params = {
        'test_read_string': only_class_params,
        'test_read_ios': only_class_params,
        'test_read_ltl': full_fvec_params,
        'test_read_write': full_fvec_params,
        'test_not_array': only_class_params,
        'test_too_many_dims': [dict(cls_type='fvec')],
        'test_wrong_dtype': only_class_params,
        'test_wrong_dtype2': only_class_params,
        'test_wrong_class': [dict(cls_type='fvec', ftype='marray'),
                             dict(cls_type='marray', ftype='fvec')],
        'test_wrong_rtype': only_class_params,
        'test_T_type': only_class_params,
        'test_short_data': [dict(cls_type='fvec')],
        'test_stride': [dict(cls_type='fvec')],
        'test_empty_write': [dict(cls_type='fvec')],
        'test_long_write': [dict(cls_type='fvec', typ='int',
                                 data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                       11, 12, 13, 14, 15]),
                            dict(cls_type='marray', typ='int',
                                 data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                       11, 12, 13, 14, 15])]
        }

    def test_read_string(self, datadir, cls_type):
        assert read(cls_type, datadir.join('test'+cls_type+'_int.dat').strpath)

    def test_read_ios(self, datadir, cls_type):
        in_ = datadir.join('test'+cls_type+'_int.dat').open()
        i = clsmap[cls_type]()
        i.read(in_)

    def test_read_ltl(self, datadir, cls_type, typ, data):

        expected = np.array(data, dtype=dtypemap[typ])
        actual = read(cls_type,
                      datadir.join('test'+cls_type+'_'+typ+'.dat').strpath)
        assert np.isclose(expected, actual.data).all()

    def test_read_write(self, tmpdir, cls_type, typ, data):

        outname = tmpdir.mkdir(cls_type).join('test_'+cls_type+'_'+typ+'.dat')

        expected = np.array(data, dtype=dtypemap[typ])
        write(outname, cls_type, typ, data)
        actual = read(cls_type, outname.strpath)
        assert np.isclose(expected, actual.data).all()

    def test_not_array(self, cls_type):
        t = clsmap[cls_type]()
        with pytest.raises(TypeError):
            t.data = 2

    def test_too_many_dims(self, cls_type):
        t = clsmap[cls_type]()
        with pytest.raises(TypeError):
            t.data = np.array([[1, 2], [1, 2]])

    def test_wrong_dtype(self, cls_type):
        t = clsmap[cls_type]()
        with pytest.raises(TypeError):
            t.data = np.array([1, 2], dtype=bool)

    def test_wrong_dtype2(self, tmpdir, cls_type):
        t = clsmap[cls_type]()
        t._data = np.array([1, 2], dtype=bool)
        of = tmpdir.mkdir(cls_type).join('test.dat').open('w')
        with pytest.raises(Exception):
            t.write(of)

    def test_wrong_class(self, datadir, cls_type, ftype):
        with pytest.raises(TypeError):
            assert read(cls_type,
                        datadir.join('test'+ftype+'_int.dat').strpath)

    def test_wrong_rtype(self, datadir, cls_type):
        with pytest.raises(TypeError):
            assert read(cls_type,
                        datadir.join('test'+cls_type+'_char.dat').strpath)

    def test_T_type(self, datadir, cls_type):
        assert read(cls_type,
                    datadir.join('test'+cls_type+'_T.dat').strpath)

    def test_short_data(self, datadir, cls_type):
        with pytest.raises(Exception):
            assert read(cls_type,
                        datadir.join('test'+cls_type+'_int_short.dat').strpath)

    def test_stride(self, datadir, cls_type):
        with pytest.raises(Exception):
            assert read(cls_type,
                        datadir.join('test'+cls_type +
                                     '_int_stride.dat').strpath)

    def test_empty_write(self, tmpdir, cls_type):
        t = clsmap[cls_type]()
        of = tmpdir.mkdir(cls_type).join('test.dat').open('w')
        with pytest.raises(Exception):
            t.write(of)

    def test_long_write(self, tmpdir, cls_type, typ, data):

        outname = tmpdir.mkdir(cls_type).join('test_'+cls_type+'_'+typ+'.dat')
        write(outname, cls_type, typ, data)
