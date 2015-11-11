"Test pyhetdex.het.fplane"

import os
import subprocess as sp

import pytest

import pyhetdex.het.fplane as fp

import settings as s


def test_ifu():
    "Test IFU object"
    ifu = fp.IFU("001", 1, 1, 0, 3, "001")

    assert ifu.ihmpid == "003"


def test_ifu_str():
    "Test IFU object string output"
    ifu = fp.IFU("001", 1, 1, 0, 3, "001")

    assert str(ifu) == "ifu: '001'; IHMP: '003'; spectrograph: '001'"


class TestFPlane(object):
    """Test the fplane class
    """

    @classmethod
    def setup_class(cls):
        """Instantiate the FPlane object
        """
        fplane_file = os.path.join(s.datadir, "fplane.txt")
        cls.fplane = fp.FPlane(fplane_file)
        n_lines = sp.check_output(['awk', '!/^#/ {print $0}', fplane_file])
        cls.n_lines = len(n_lines.splitlines())

        return cls

    def test_size_dict(self):
        """Test the size of the ifu dictionary"""
        assert len(self.fplane.difus) == self.n_lines

    def test_size_keys(self):
        """Test the size of the keys of the ifu dictionary"""
        with pytest.warns(DeprecationWarning):
            assert len(self.fplane.ids) == self.n_lines

    def test_size_values(self):
        """Test the size of the values of the ifu dictionary"""
        assert len(self.fplane.ifus) == self.n_lines

    def test_ids(self):
        """Test that the ids are correct"""
        assert (sorted(self.fplane.ids) ==
                ["{0:03d}".format(i+1) for i in range(self.n_lines)])


def test_custom_IFU():
    "Basic customisation of the IFU object"
    class _MyIFU(fp.IFU):
        "test custom IFU class"
        def __init__(self, ifuid, x, y, xid, yid, specid):
            super(_MyIFU, self).__init__(ifuid, x, y, xid, yid, specid)
            self.mod_id = "1" + self.ifuid

    fplane_file = os.path.join(s.datadir, "fplane.txt")
    fplane = fp.FPlane(fplane_file, ifu_class=_MyIFU)
    mod_ids = [ifu.mod_id for ifu in fplane.ifus]
    assert (sorted(mod_ids) ==
            ["{0:04d}".format(i+1001) for i in range(len(fplane.ids))])
