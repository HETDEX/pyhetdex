"""
Test the reconstruction of the IFU head
"""

from __future__ import print_function, absolute_import

import glob
import os

import pytest

from pyhetdex.het import dither, ifu_centers
import pyhetdex.het.reconstruct_ifu as rifu

import settings as s

dither_fast = os.path.join(s.datadir, "dither_fast_SIMDEX-4000-obs-1_046.txt")
dither_file = os.path.join(s.datadir, "dither_SIMDEX-4000-obs-1_046.txt")
dither_other = os.path.join(s.datadir,
                            "dither_other_SIMDEX-4000-obs-1_046.txt")

ifucenter_file = os.path.join(s.datadir, "IFUcen_HETDEX.txt")
ifucenter_fail = os.path.join(s.datadir, "IFUcen_HETDEX_fail.txt")
ifucenter_missf = os.path.join(s.datadir, "IFUcen_HETDEX_missf.txt")


class TestIFUCenters(object):
    "Parse the ifu center file"

    @classmethod
    def setup_class(cls):
        cls.ifucen = ifu_centers.IFUCenter(ifucenter_file)
        return cls

    def test_channels(self):
        "Test the channels number and names"
        channels = self.ifucen.channels
        assert len(channels) == 2
        assert sorted(channels) == ['L', 'R']

    def test_L_nfibers(self):
        "Test the number of fibers in the L channel"
        nL1 = self.ifucen.n_fibers['L']
        nL2 = len(self.ifucen.fib_number['L'])
        assert nL1 == nL2
        assert nL1 == 224

    def test_R_nfibers(self):
        "Test the number of fibers in the R channel"
        nR1 = self.ifucen.n_fibers['R']
        nR2 = len(self.ifucen.fib_number['R'])
        assert nR1 == nR2
        assert nR1 == 224

    @pytest.mark.xfail(raises=ifu_centers.IFUCenterError,
                       reason="Test failures in parsing the IFUcen file")
    def test_fail(self):
        "Test comments, negative or non numeric fiber number and failure"
        ifu_centers.IFUCenter(ifucenter_fail)


# TODO: check that the reconstruction does a proper job checking the outputs

class TestReconstruction(object):
    "Test various ways to do the reconstruction"

    def test_init(self):
        "Reconstruction from existing ifu center and dither objects"
        ifucen = ifu_centers.IFUCenter(ifucenter_file)
        d = dither.ParseDither(dither_fast)

        recifu = rifu.ReconstructedIFU(ifucen, d, fe_prefix='')
        x, y, flux = recifu.reconstruct()
        assert len(x) == len(y)
        assert len(x) == len(flux)

    def test_from_file(self):
        "Reconstruction from ifu center and dither files (full basename)"
        recifu = rifu.ReconstructedIFU.from_files(ifucenter_file, dither_fast,
                                                  fe_prefix='')
        # return recifu
        pass

    def test_from_file_fe(self):
        "Reconstruction from ifu center and dither files (partial basenames)"
        recifu = rifu.ReconstructedIFU.from_files(ifucenter_file,
                                                  dither_file,
                                                  fe_prefix='fast_')
        pass

    def test_no_dither_file(self):
        "Reconstruction from the fiber extracted files (no dither file)"
        fextract = glob.glob(os.path.join(s.datadir, "fast_SIM*D1*.fits"))
        recifu = rifu.ReconstructedIFU.from_files(ifucenter_file,
                                                  fextract=fextract)

    def test_fextracts(self):
        "Reconstruction from the fiber extracted files (with dither file)"
        fextract = glob.glob(os.path.join(s.datadir, "fast_SIM*D*.fits"))
        recifu = rifu.ReconstructedIFU.from_files(ifucenter_file, dither_other,
                                                  fextract=fextract)
        pass

    @pytest.mark.xfail(raises=rifu.ReconstructIOError,
                       reason="Mismatch between dither and provided files")
    def test_fail_no_dither_file(self):
        "Reconstruction from 6 fe files and empty dither file fails"
        fextract = glob.glob(os.path.join(s.datadir, "fast_SIM*D*.fits"))
        recifu = rifu.ReconstructedIFU.from_files(ifucenter_file,
                                                  fextract=fextract)
        pass

    @pytest.mark.xfail(raises=rifu.ReconstructValueError,
                       reason="The IFUcen file alone it's not enough")
    def test_no_dither_no_fextract1(self):
        """Reconstruction from the ifu center file alone fails"""
        recifu = rifu.ReconstructedIFU.from_files(ifucenter_file)

    @pytest.mark.xfail(raises=rifu.ReconstructValueError,
                       reason="The IFUcen file and empty dither file")
    def test_no_dither_no_fextract2(self):
        """Reconstruction from the ifu center and empty dither fails"""
        ifucen = ifu_centers.IFUCenter(ifucenter_file)
        d = dither.EmptyDither()
        recifu = rifu.ReconstructedIFU(ifucenter_file, d)

    @pytest.mark.xfail(raises=rifu.ReconstructIOError,
                       reason="Two of the input files are for the same file"
                       "and dither")
    def test_repeated_dither_channel(self):
        "Fails when two files are for the same dither and channel"
        fextract = glob.glob(os.path.join(s.datadir, "fast_SIM*D1*.fits"))
        recifu = rifu.ReconstructedIFU.from_files(ifucenter_file, dither_file,
                                                  fextract=fextract*3)

    @pytest.mark.xfail(raises=rifu.ReconstructIOError,
                       reason="Mismatching header keywords")
    def test_missmatch_header_info(self):
        "Fails when header entries don't match with expected values"
        fextract = glob.glob(os.path.join(s.datadir, "fast_SIM*D2*.fits"))
        recifu = rifu.ReconstructedIFU.from_files(ifucenter_file,
                                                  fextract=fextract)

    @pytest.mark.xfail(raises=rifu.ReconstructIndexError,
                       reason="Mismatching in the number of fibers")
    def test_fib_missmatch(self):
        "Fails for number of fiber mismatch"
        rifu.ReconstructedIFU.from_files(ifucenter_missf, dither_fast,
                                         fe_prefix='')


if __name__ == "__main__":
    tr = TestReconstruction()
    rifu = tr.test_from_file()
    x, y, f = rifu.reconstruct(4000, 5000)
    # import IPython
    # IPython.embed()
