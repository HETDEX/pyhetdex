"""
Test the reconstruction of the IFU head
"""

from __future__ import print_function, absolute_import

import glob
import nose.tools as nt
import os

from pyhetdex import het
import pyhetdex.het.reconstruct_ifu as rifu

import settings as s

dither_file = os.path.join(s.datadir, "dither.txt")
ifucenter_file = os.path.join(s.datadir, "IFUcen_HETDEX.txt")
# this dither file contains already the fiber extracted base name
ditherfe_file = os.path.join(s.datadir, "dither_fe.txt")


class TestDither(object):
    "Parse the dither files"
    def test_empty_dithers(self):
        "Empty dither"
        dithers = het.dither.EmptyDither()
        nt.assert_equal(len(dithers.dithers), 1)

    def test_dithers(self):
        "Parse the dither file"
        dithers = het.dither.ParseDither(dither_file)
        nt.assert_equal(len(dithers.dithers), 3)


class TestIFUCenters(object):
    "Parse the ifu center file"

    @classmethod
    def setup_class(cls):
        cls.ifucen = het.ifu_centers.IFUCenter(ifucenter_file)
        return cls

    def test_channels(self):
        "Test the channels number and names"
        channels = self.ifucen.channels
        nt.assert_equal(len(channels), 2)
        nt.assert_equal(sorted(channels), ['L', 'R'])

    def test_L_nfibers(self):
        "Test the number of fibers in the L channel"
        nL1 = self.ifucen.n_fibers['L']
        nL2 = len(self.ifucen.fib_number['L'])
        nt.assert_equal(nL1, nL2)
        nt.assert_equal(nL1, 224)

    def test_R_nfibers(self):
        "Test the number of fibers in the R channel"
        nR1 = self.ifucen.n_fibers['R']
        nR2 = len(self.ifucen.fib_number['R'])
        nt.assert_equal(nR1, nR2)
        nt.assert_equal(nR1, 224)


# TODO: check that the reconstruction does a proper job checking the outputs
class TestReconstruction(object):
    "Test various ways to do the reconstruction"

    def test_init(self):
        "Reconstruction from existing ifu center and dither objects"
        ifucen = het.ifu_centers.IFUCenter(ifucenter_file)
        dither = het.dither.ParseDither(dither_file)

        recifu = rifu.ReconstructedIFU(ifucen, dither)
        x, y, flux = recifu.reconstruct()
        nt.assert_equal(len(x), len(y))
        nt.assert_equal(len(x), len(flux))
        pass

    def test_from_file(self):
        "Reconstruction from ifu center and dither files"
        recifu = rifu.ReconstructedIFU.from_files(ifucenter_file, dither_file)
        pass

    def test_from_file_fe(self):
        """Reconstruction from ifu center and dither files (fe basenames)"""
        recifu = rifu.ReconstructedIFU.from_files(ifucenter_file,
                                                  ditherfe_file, fe_prefix='')
        pass

    def test_no_dither_file(self):
        "Reconstruction from the fiber extracted files and not dither file"
        fextract = glob.glob(os.path.join(s.datadir, "FeSIM*D1*.fits"))
        recifu = rifu.ReconstructedIFU.from_files(ifucenter_file,
                                                  fextract=fextract)
        pass

    def test_fextracts(self):
        "Reconstruction from the fiber extracted files and not dither file"
        fextract = glob.glob(os.path.join(s.datadir, "FeSIM*D*.fits"))
        recifu = rifu.ReconstructedIFU.from_files(ifucenter_file, dither_file,
                                                  fextract=fextract)
        pass

    @nt.raises(rifu.ReconstructIOError)
    def test_fail_no_dither_file(self):
        "Reconstruction from 6 fe files and empty dither file fails"
        fextract = glob.glob(os.path.join(s.datadir, "FeSIM*D*.fits"))
        recifu = rifu.ReconstructedIFU.from_files(ifucenter_file,
                                                  fextract=fextract)
        pass

    @nt.raises(rifu.ReconstructValueError)
    def test_no_dither_no_fextract1(self):
        """Reconstruction from the ifu center file alone fails"""
        recifu = rifu.ReconstructedIFU.from_files(ifucenter_file)

    @nt.raises(rifu.ReconstructValueError)
    def test_no_dither_no_fextract2(self):
        """Reconstruction from the ifu center and empty dither fails"""
        ifucen = het.ifu_centers.IFUCenter(ifucenter_file)
        dither = het.dither.EmptyDither()
        recifu = rifu.ReconstructedIFU(ifucenter_file, dither)
