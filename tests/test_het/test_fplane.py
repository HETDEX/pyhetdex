"Test pyhetdex.het.fplane"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import subprocess as sp

import pytest

import pyhetdex.het.fplane as fp


def test_ifu():
    "Test IFU object"
    ifu = fp.IFU("013", 1, 1, 0, 0, "001", 0, 0)

    assert ifu.xid == 1
    assert ifu.yid == 3


def test_ifu_str():
    "Test IFU object string output"
    ifu = fp.IFU("013", 1, 1, 53, 0, "001", 0, 0)

    assert str(ifu) == "ifuslot: '013'; ifuid: '001'; specid: '53'"


class TestFPlane(object):
    """Test the fplane class
    """

    @pytest.fixture(scope='class')
    def fplane(self, fplane_file):
        """Instantiate the FPlane object. Returns it and the number of lines in
        it
        """
        return fp.FPlane(fplane_file.strpath)

    @pytest.fixture(scope='class')
    def n_lines(self, fplane_file):
        'return the number of lines in the fplane file'
        n_lines = sp.check_output(['awk', '!/^#/ {print $0}',
                                   fplane_file.strpath])
        n_lines = len(n_lines.splitlines())

        return n_lines

    def test_ifuslot_type(self):
        """Test error if ifuslot is of wrong type"""
        with pytest.raises(TypeError):
            fp.IFU(2, 1, 1, 1, 1, '111', 0, 0)

    def test_ihmpid(self, fplane, n_lines):
        """Test the size of the ifu dictionary"""
        with pytest.warns(DeprecationWarning):
            assert len(fplane.ihmpids) == n_lines
        with pytest.warns(DeprecationWarning):
            ifu = fplane.by_ihmpid('073')
            assert ifu.ifuid == '023'
            with pytest.raises(KeyError):
                fplane.by_ihmpid('001')

    def test_ifuid(self, fplane):
        """Test the by_ifuid function"""
        ifu = fplane.by_ifuid('023')
        assert ifu.ifuslot == '073'
        with pytest.raises(KeyError):
            fplane.by_ifuid('200')

    def test_ifuslot(self, fplane):
        """Test the by_ifuslot function"""
        ifu = fplane.by_ifuslot('073')
        assert ifu.ifuid == '023'
        with pytest.raises(KeyError):
            fplane.by_ifuslot('001')

    def test_slotpos(self, fplane):
        """Test the by_slotpos function"""
        ifu = fplane.by_slotpos(7, 3)
        assert ifu.ifuid == '023'
        with pytest.raises(fp.NoIFUError):
            fplane.by_slotpos(11, 12)

    def test_specid(self, fplane):
        """Test the by_specid function"""
        ifu = fplane.by_specid(4)
        assert ifu.ifuid == '023'
        with pytest.raises(fp.NoIFUError):
            fplane.by_specid(100)

    def test_byid(self, fplane):
        """Test the by_specid function"""
        ifu = fplane.by_id('023', 'ifuid')
        assert ifu.ifuslot == '073'
        ifu = fplane.by_id('073', 'ifuslot')
        assert ifu.ifuid == '023'
        with pytest.warns(DeprecationWarning):
            ifu = fplane.by_id('073', 'ihmpid')
            assert ifu.ifuid == '023'
        ifu = fplane.by_id(4, 'specid')
        assert ifu.ifuslot == '073'
        with pytest.raises(fp.UnknownIDTypeError):
            fplane.by_id(1, 'lall')

    def test_ifuids_size(self, fplane, n_lines):
        """Test the size of the ifu dictionary"""
        assert len(fplane.ifuids) == n_lines

    def test_specids_size(self, fplane, n_lines):
        """Test the size of the ifu dictionary"""
        assert len(fplane.specids) == n_lines

    def test_size_dict(self, fplane, n_lines):
        """Test the size of the ifu dictionary"""
        assert len(fplane.difus) == n_lines

    def test_size_keys(self, fplane, n_lines):
        """Test the size of the keys of the ifu dictionary"""
        assert len(fplane.ifus) == n_lines

    def test_size_values(self, fplane, n_lines):
        """Test the size of the values of the ifu dictionary"""
        assert len(fplane.ifus) == n_lines

    def test_ifuslots(self, fplane):
        """Test that the ids are correct"""
        slots = ['013', '014', '015', '016', '021', '022', '023', '024', '025',
                 '026', '027', '028', '030', '031', '032', '033', '034', '035',
                 '036', '037', '038', '039', '040', '041', '042', '043', '044',
                 '045', '046', '047', '048', '049', '050', '051', '052', '053',
                 '057', '058', '059', '060', '061', '062', '063', '067', '068',
                 '069', '070', '071', '072', '073', '074', '075', '076', '077',
                 '078', '079', '080', '081', '082', '083', '084', '085', '086',
                 '087', '088', '089', '091', '092', '093', '094', '095', '096',
                 '097', '098', '103', '104', '105', '106']
        assert (sorted(fplane.ifuslots) == slots)

    def test_missing_ius(self, fplane):
        """Test that the ids are correct"""
        ifu = fplane.by_ifuslot('013')
        assert ifu.ifuid == 'N01'


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
