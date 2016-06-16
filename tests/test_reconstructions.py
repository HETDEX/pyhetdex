"""
Test the reconstruction of the IFU head
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import glob
import os

import pytest

from pyhetdex.het import dither, ifu_centers
import pyhetdex.het.reconstruct_ifu as rifu

import conftest
import settings as s

dither_fast = os.path.join(s.datadir, "dither_fast_SIMDEX-4000-obs-1_046.txt")
dither_file = os.path.join(s.datadir, "dither_SIMDEX-4000-obs-1_046.txt")
dither_other = os.path.join(s.datadir,
                            "dither_other_SIMDEX-4000-obs-1_046.txt")

ifucenter_file = os.path.join(s.datadir, "IFUcen_HETDEX.txt")
ifucenter_fail = os.path.join(s.datadir, "IFUcen_HETDEX_fail.txt")
ifucenter_missid = os.path.join(s.datadir, "IFUcen_HETDEX_missid.txt")
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

    @pytest.mark.xfail(raises=ifu_centers.IFUCenterError,
                       reason="Test failures in parsing the IFUcen file")
    def test_missingid(self):
        "Test missing ID string in header"
        ifu_centers.IFUCenter(ifucenter_missid)


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


dist_l = 'distortion_L.dist'
dist_r = 'distortion_R.dist'

inputfilenames = ['20151025T122555_103LL_sci.fits',
                  '20151025T122555_103LU_sci.fits',
                  '20151025T122555_103RL_sci.fits',
                  '20151025T122555_103RU_sci.fits']

inputfilenames_l = ['20151025T122555_103LL_sci.fits',
                    '20151025T122555_103LU_sci.fits']

inputfilenames_r = ['20151025T122555_103RL_sci.fits',
                    '20151025T122555_103RU_sci.fits']


class TestQuickReconstruction(object):
    "Test various ways to do the reconstruction"

    def test_init(self, datadir, tmpdir):
        "Quick Reconstruction from existing ifu center and dither objects"

        infiles = [datadir.join(i).strpath for i in inputfilenames]
        dl = datadir.join(dist_l).strpath
        dr = datadir.join(dist_r).strpath

        rimg = rifu.QuickReconstructedIFU(ifucenter_file, dist_r=dr, dist_l=dl)

        actual = tmpdir.join('qrecon.fits').strpath

        rimg.reconstruct(infiles)
        rimg.write(actual)

        expected = datadir.join('reconstructed.fits').strpath

        assert conftest.compare_fits(expected, actual)

    def test_pscale_setter(self, datadir, tmpdir):
        dl = datadir.join(dist_l).strpath
        dr = datadir.join(dist_r).strpath

        rimg = rifu.QuickReconstructedIFU(ifucenter_file, dist_r=dr, dist_l=dl)
        rimg.pscale = 0.25

    @pytest.mark.xfail(raises=rifu.ReconstructError,
                       reason='No reconstrution happened')
    def test_write_error(self, datadir, tmpdir):
        dl = datadir.join(dist_l).strpath
        dr = datadir.join(dist_r).strpath

        rimg = rifu.QuickReconstructedIFU(ifucenter_file, dist_r=dr, dist_l=dl)

        actual = tmpdir.join('qrecon.fits').strpath

        # Test for exception on write without reconstruct
        rimg.write(actual)

    @pytest.mark.xfail(raises=rifu.ReconstructValueError,
                       reason='No ifu cen file provided')
    def test_missing_ifucen(self, datadir, tmpdir):
        dl = datadir.join(dist_l).strpath
        dr = datadir.join(dist_r).strpath

        rifu.QuickReconstructedIFU(None, dist_r=dr, dist_l=dl)

    @pytest.mark.xfail(raises=rifu.ReconstructValueError,
                       reason='No distortion file provided')
    def test_no_dist(self, datadir, tmpdir):

        rifu.QuickReconstructedIFU(ifucenter_file)

    def test_left_dist(self, datadir, tmpdir):
        dl = datadir.join(dist_l).strpath

        rifu.QuickReconstructedIFU(ifucenter_file, dist_l=dl)

    def test_right_dist(self, datadir, tmpdir):
        dr = datadir.join(dist_r).strpath

        rifu.QuickReconstructedIFU(ifucenter_file,
                                   dist_r=dr)

    @pytest.mark.xfail(raises=rifu.ReconstructValueError,
                       reason='Wrong distortion for the input files')
    def test_missing_dist(self, datadir, tmpdir):
        ''' Test combination of left spectrograph images with right
        spectrograph distortion
        '''
        infiles = [datadir.join(i).strpath for i in inputfilenames_l]
        dr = datadir.join(dist_r).strpath

        rimg = rifu.QuickReconstructedIFU(ifucenter_file, dist_r=dr)
        rimg.reconstruct(infiles)

    def test_wrong_ifu(self, datadir, tmpdir):
        ''' Test combination of left spectrograph images with right
        spectrograph distortion
        '''
        filenames = ['20151025T122555_104LL_sci.fits',
                     '20151025T122555_103LU_sci.fits']
        infiles = [datadir.join(i).strpath for i in filenames]
        dl = datadir.join(dist_l).strpath

        rimg = rifu.QuickReconstructedIFU(ifucenter_file,
                                          dist_l=dl)
        rimg.reconstruct(infiles)

    def test_no_overscan(self, datadir, tmpdir):
        '''Test reconstruction without overscan subtraction'''
        infiles = [datadir.join(i).strpath for i in inputfilenames_r]

        dr = datadir.join(dist_r).strpath

        rimg = rifu.QuickReconstructedIFU(ifucenter_file,
                                          dist_r=dr)
        rimg.reconstruct(infiles, subtract_overscan=False)

    def test_combined_img(self, datadir, tmpdir):
        '''Test reconstruction without overscan subtraction '''
        infile = [datadir.join('masterarc_080R.fits').strpath]
        dr = datadir.join(dist_r).strpath

        rimg = rifu.QuickReconstructedIFU(ifucenter_file,
                                          dist_r=dr)

        rimg.reconstruct(infile, subtract_overscan=False)

    def test_arg_missing_ifucen(self):
        with pytest.raises(SystemExit):
            rifu.argument_parser([])

    def test_arg_missing_files(self):
        with pytest.raises(SystemExit):
            rifu.argument_parser(['ifufile'])

    def test_arg_required(self):
        a = rifu.argument_parser(['ifufile', 'file1', 'file2'])
        assert a.ifucen == 'ifufile'
        assert a.files == ['file1', 'file2']

    def test_arg_outfile(self):
        a = rifu.argument_parser(['-o', 'out', 'ifufile', 'file1'])
        assert a.outfile == 'out'

    def test_arg_outfile_long(self):
        a = rifu.argument_parser(['--outfile', 'out', 'ifufile', 'file1'])
        assert a.outfile == 'out'

    def test_arg_ldist(self):
        a = rifu.argument_parser(['-l', 'ldist', 'ifufile', 'file1'])
        assert a.ldist == 'ldist'

    def test_arg_ldist_long(self):
        a = rifu.argument_parser(['--ldist', 'ldist', 'ifufile', 'file1'])
        assert a.ldist == 'ldist'

    def test_arg_rdist(self):
        a = rifu.argument_parser(['-r', 'rdist', 'ifufile', 'file1'])
        assert a.rdist == 'rdist'

    def test_arg_rdistlong(self):
        a = rifu.argument_parser(['--rdist', 'rdist', 'ifufile', 'file1'])
        assert a.rdist == 'rdist'

    def test_arg_scale(self):
        a = rifu.argument_parser(['-s', '1.2', 'ifufile', 'file1'])
        assert a.scale == 1.2

    def test_arg_scale_long(self):
        a = rifu.argument_parser(['--scale', '1.2', 'ifufile', 'file1'])
        assert a.scale == 1.2

    def test_arg_full(self):
        argv = ['-o', 'out',
                '--ldist', 'distl',
                '--rdist', 'distr',
                '--s', '1.2', 'ifufile', 'file1', 'file3']
        a = rifu.argument_parser(argv)
        assert a.outfile == 'out'
        assert a.ldist == 'distl'
        assert a.rdist == 'distr'
        assert a.scale == 1.2
        assert a.ifucen == 'ifufile'
        assert a.files == ['file1', 'file3']

    def test_entry_point(self, datadir, tmpdir):
        "Quick Reconstruction from existing ifu center and dither objects"

        infiles = [datadir.join(i).strpath for i in inputfilenames]
        dl = datadir.join(dist_l).strpath
        dr = datadir.join(dist_r).strpath
        actual = tmpdir.join('qrecon.fits').strpath

        argv = ['-s', '0.25', '-l', dl, '-r', dr, '-o', actual, ifucenter_file]
        argv.extend(infiles)

        rifu.create_quick_reconstruction(argv)

        expected = datadir.join('reconstructed.fits').strpath

        assert conftest.compare_fits(expected, actual)


if __name__ == "__main__":
    tr = TestReconstruction()
    rifu = tr.test_from_file()
    x, y, f = rifu.reconstruct(4000, 5000)
    # import IPython
    # IPython.embed()
