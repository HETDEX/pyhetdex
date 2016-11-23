"Test pyhetdex.het.fplane"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest

import pyhetdex.het.fplane as fp

parametrize = pytest.mark.parametrize


@pytest.fixture
def fplane_lines():
    '''Returns the lines that go into the fplane file as a list of strings'''
    lines = ['# a comment',
             '001  0  0 02 003 004 0.0 1.0',
             '011 10 10 00 000 000 0.0 1.0',
             ]
    return lines


@pytest.fixture
def slots():
    '''slots used in the fplane file'''
    return ['001', '011']


@pytest.fixture
def fplane_file(tmpdir, fplane_lines):
    '''Create a fplane file suitable to test the module. Return the file as a
    py.path.local instance'''
    _fplane = tmpdir.join('fplane.txt')

    _fplane.write('\n'.join(fplane_lines))

    return _fplane


@pytest.fixture
def fplane(fplane_file):
    """Instantiate the FPlane object. Returns it and the number of lines in
    it
    """
    return fp.FPlane(fplane_file.strpath)


@pytest.fixture
def n_lines(fplane_lines):
    'return the number of lines in the fplane file'
    n_lines = len(list(filter(lambda x: not x.startswith('#'), fplane_lines)))

    return n_lines


def test_ifu():
    "Test IFU object"
    ifu = fp.IFU("013", 1, 1, 0, 0, "001", 0, 0)

    assert ifu.xid == 1
    assert ifu.yid == 3


def test_ifu_str():
    "Test IFU object string output"
    ifu = fp.IFU("013", 1, 1, 53, 0, "001", 0, 0)

    assert str(ifu) == "ifuslot: '013'; ifuid: '001'; specid: '53'"


def test_ifuslot_type():
    """Test error if ifuslot is of wrong type"""
    with pytest.raises(TypeError):
        fp.IFU(2, 1, 1, 1, 1, '111', 0, 0)


def test_ihmpid(fplane, n_lines):
    """Test the size of the ifu dictionary"""
    with pytest.warns(DeprecationWarning):
        assert len(fplane.ihmpids) == n_lines
    with pytest.warns(DeprecationWarning):
        ifu = fplane.by_ihmpid('001')
        assert ifu.ifuid == '004'
        with pytest.raises(KeyError):
            fplane.by_ihmpid('200')


def test_ifuid(fplane):
    """Test the by_ifuid function"""
    ifu = fplane.by_ifuid('004')
    assert ifu.ifuslot == '001'
    with pytest.raises(KeyError):
        fplane.by_ifuid('200')


def test_ifuslot(fplane):
    """Test the by_ifuslot function"""
    ifu = fplane.by_ifuslot('001')
    assert ifu.ifuid == '004'
    with pytest.raises(KeyError):
        fplane.by_ifuslot('200')


def test_slotpos(fplane):
    """Test the by_slotpos function"""
    ifu = fplane.by_slotpos(0, 1)
    assert ifu.ifuid == '004'
    with pytest.raises(fp.NoIFUError):
        fplane.by_slotpos(11, 12)


def test_specid(fplane):
    """Test the by_specid function"""
    ifu = fplane.by_specid(2)
    assert ifu.ifuid == '004'
    with pytest.raises(fp.NoIFUError):
        fplane.by_specid(200)


def test_byid(fplane):
    """Test the by_specid function"""
    ifu = fplane.by_id('004', 'ifuid')
    assert ifu.ifuslot == '001'
    ifu = fplane.by_id('001', 'ifuslot')
    assert ifu.ifuid == '004'
    with pytest.warns(DeprecationWarning):
        ifu = fplane.by_id('001', 'ihmpid')
        assert ifu.ifuid == '004'
    ifu = fplane.by_id(2, 'specid')
    assert ifu.ifuslot == '001'
    with pytest.raises(fp.UnknownIDTypeError):
        fplane.by_id(1, 'lall')


def test_ifuids_size(fplane, n_lines):
    """Test the size of the ifu dictionary"""
    assert len(fplane.ifuids) == n_lines


def test_specids_size(fplane, n_lines):
    """Test the size of the ifu dictionary"""
    assert len(fplane.specids) == n_lines


def test_size_dict(fplane, n_lines):
    """Test the size of the ifu dictionary"""
    assert len(fplane.difus) == n_lines


def test_size_keys(fplane, n_lines):
    """Test the size of the keys of the ifu dictionary"""
    assert len(fplane.ifus) == n_lines


def test_size_values(fplane, n_lines):
    """Test the size of the values of the ifu dictionary"""
    assert len(fplane.ifus) == n_lines


def test_ifuslots(fplane, slots):
    """Test that the ids are correct"""
    assert sorted(fplane.ifuslots) == slots


def test_missing_ius(fplane_file):
    """Test that the missing ids are correctly handled"""
    fplane = fp.FPlane(fplane_file.strpath)
    ifu = fplane.by_ifuslot('011')
    assert ifu.specid == -1
    assert ifu.ifuid == 'N01'

    fplane = fp.FPlane(fplane_file.strpath, empty_specid='11')
    ifu = fplane.by_ifuslot('011')
    assert ifu.specid == 0
    assert ifu.ifuid == 'N01'

    fplane = fp.FPlane(fplane_file.strpath, empty_ifuid='111')
    ifu = fplane.by_ifuslot('011')
    assert ifu.specid == -1
    assert ifu.ifuid == '000'


@parametrize('skip_id, n_ifus',
             [([], 2), (['001', ], 1),
              (['011', ], 1), (['021', ], 2)])
def test_skip_ifuslot(fplane_file, skip_id, n_ifus):
    '''Test skipping one of the IFUs giving the IFU slot'''
    fplane = fp.FPlane(fplane_file.strpath, exclude_ifuslot=skip_id)

    assert len(fplane.ifus) == n_ifus


@parametrize('skip_empty, n_ifus', [(False, 2), (True, 1)])
@parametrize('empty_specid, empty_ifuid, ',
             [('00', '000'), ('other', '000'), ('00', 'other')])
def test_skip_empty(fplane_file, empty_specid, empty_ifuid, skip_empty,
                    n_ifus):
    '''Test skipping one of the IFUs if the SPECID or the IFUID is empty'''
    fplane = fp.FPlane(fplane_file.strpath, empty_specid=empty_specid,
                       empty_ifuid=empty_ifuid, skip_empty=skip_empty)

    assert len(fplane.ifus) == n_ifus


def test_custom_IFU(datadir):
    "Basic customisation of the IFU object"
    class _MyIFU(fp.IFU):
        "test custom IFU class"
        def __init__(self, ifuslot, x, y, specid, specslot,
                     ifuid, ifurot, platescl):
            super(_MyIFU, self).__init__(ifuslot, x, y, specid, specslot,
                                         ifuid, ifurot, platescl)
            self.mod_id = "1" + self.ifuslot

    fplane_file = datadir.join("fplane.txt").strpath
    fplane = fp.FPlane(fplane_file, ifu_class=_MyIFU)
    mod_ids = [ifu.mod_id for ifu in fplane.ifus]
    slots = ['1013', '1014', '1015', '1016', '1021', '1022', '1023', '1024',
             '1025', '1026', '1027', '1028', '1030', '1031', '1032', '1033',
             '1034', '1035', '1036', '1037', '1038', '1039', '1040', '1041',
             '1042', '1043', '1044', '1045', '1046', '1047', '1048', '1049',
             '1050', '1051', '1052', '1053', '1057', '1058', '1059', '1060',
             '1061', '1062', '1063', '1067', '1068', '1069', '1070', '1071',
             '1072', '1073', '1074', '1075', '1076', '1077', '1078', '1079',
             '1080', '1081', '1082', '1083', '1084', '1085', '1086', '1087',
             '1088', '1089', '1091', '1092', '1093', '1094', '1095', '1096',
             '1097', '1098', '1103', '1104', '1105', '1106']
    assert (sorted(mod_ids) == slots)
