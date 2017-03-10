"""
Test the reconstruction of the IFU head
"""
from __future__ import (absolute_import, division, print_function)
# , unicode_literals)

from astropy.io import fits
import numpy as np
import pytest

from pyhetdex.het import dither, ifu_centers
import pyhetdex.het.reconstruct_ifu as rifu

parametrize = pytest.mark.parametrize


@pytest.fixture
def ifucen(ifucenter_file):
    'create and return the ifu center file object'
    return ifu_centers.IFUCenter(ifucenter_file.strpath)


def test_recon_init(ifucenter_file, dither_fast):
    "Reconstruction from existing ifu center and dither objects"
    ifucen = ifu_centers.IFUCenter(ifucenter_file.strpath)
    d = dither.ParseDither(dither_fast.strpath)

    recifu = rifu.ReconstructedIFU(ifucen, d, fe_prefix='')
    x, y, flux = recifu.reconstruct()
    assert len(x) == len(y)
    assert len(x) == len(flux)


def test_recon_from_file(ifucenter_file, dither_fast):
    "Reconstruction from ifu center and dither files (full basename)"
    rifu.ReconstructedIFU.from_files(ifucenter_file.strpath,
                                     dither_fast.strpath, fe_prefix='')
    pass


def test_recon_from_file_fe(ifucenter_file, dither_file):
    "Reconstruction from ifu center and dither files (partial basenames)"
    rifu.ReconstructedIFU.from_files(ifucenter_file.strpath,
                                     dither_file.strpath, fe_prefix='fast_')
    pass


def test_recon_no_dither_file(datadir, ifucenter_file):
    "Reconstruction from the fiber extracted files (no dither file)"
    fextract = [i.strpath for i in datadir.visit("fast_SIM*D1*.fits")]
    rifu.ReconstructedIFU.from_files(ifucenter_file.strpath,
                                     fextract=fextract)


def test_recon_fextracts(datadir, ifucenter_file, dither_other):
    "Reconstruction from the fiber extracted files (with dither file)"
    fextract = [i.strpath for i in datadir.visit("fast_SIM*D*.fits")]
    rifu.ReconstructedIFU.from_files(ifucenter_file.strpath,
                                     dither_other.strpath, fextract=fextract)


@pytest.mark.xfail(raises=rifu.ReconstructIOError,
                   reason="Mismatch between dither and provided files")
def test_recon_fail_no_dither_file(datadir, ifucenter_file):
    "Reconstruction from 6 fe files and empty dither file fails"
    fextract = [i.strpath for i in datadir.visit("fast_SIM*D*.fits")]
    rifu.ReconstructedIFU.from_files(ifucenter_file.strpath, fextract=fextract)


@pytest.mark.xfail(raises=rifu.ReconstructValueError,
                   reason="The IFUcen file alone it's not enough")
def test_recon_no_dither_no_fextract1(ifucenter_file):
    """Reconstruction from the ifu center file alone fails"""
    rifu.ReconstructedIFU.from_files(ifucenter_file)


@pytest.mark.xfail(raises=rifu.ReconstructValueError,
                   reason="The IFUcen file and empty dither file")
def test_recon_no_dither_no_fextract2(ifucen):
    """Reconstruction from the ifu center and empty dither fails"""
    d = dither.EmptyDither()
    rifu.ReconstructedIFU(ifucen, d)


@pytest.mark.xfail(raises=rifu.ReconstructIOError,
                   reason="Two of the input files are for the same file"
                   "and dither")
def test_recon_repeated_dither_channel(datadir, ifucenter_file, dither_file):
    "Fails when two files are for the same dither and channel"
    fextract = [i.strpath for i in datadir.visit("fast_SIM*D1*.fits")]
    rifu.ReconstructedIFU.from_files(ifucenter_file.strpath,
                                     dither_file.strpath, fextract=fextract*3)


@pytest.mark.xfail(raises=rifu.ReconstructIOError,
                   reason="Mismatching header keywords")
def test_recon_missmatch_header_info(datadir, ifucenter_file):
    "Fails when header entries don't match with expected values"
    fextract = [i.strpath for i in datadir.visit("fast_SIM*D2*.fits")]
    rifu.ReconstructedIFU.from_files(ifucenter_file.strpath, fextract=fextract)


@pytest.mark.xfail(raises=rifu.ReconstructIndexError,
                   reason="Mismatching in the number of fibers")
def test_recon_fib_missmatch(ifucenter_missf, dither_fast):
    "Fails for number of fiber mismatch"
    rifu.ReconstructedIFU.from_files(ifucenter_missf.strpath,
                                     dither_fast.strpath, fe_prefix='')


dist_l = 'distortion_L.dist'
dist_r = 'distortion_R.dist'

inputfilenames_l = ['20151025T122555_103LL_sci.fits',
                    '20151025T122555_103LU_sci.fits']

inputfilenames_r = ['20151025T122555_103RL_sci.fits',
                    '20151025T122555_103RU_sci.fits']

inputfilenames = inputfilenames_l + inputfilenames_r


class TestQuickReconstruction(object):
    "Test various ways to do the reconstruction"

    @parametrize('do_not_scale_image_data', [True, False])
    def test_init(self, datadir, tmpdir, ifucenter_file, compare_fits,
                  do_not_scale_image_data):
        "Quick Reconstruction from existing ifu center and dither objects"

        infiles = [datadir.join(i).strpath for i in inputfilenames]
        dl = datadir.join(dist_l).strpath
        dr = datadir.join(dist_r).strpath

        rimg = rifu.QuickReconstructedIFU(ifucenter_file.strpath, dist_r=dr,
                                          dist_l=dl)

        actual = tmpdir.join('qrecon.fits').strpath

        image = rimg.reconstruct(infiles,
                               do_not_scale_image_data=do_not_scale_image_data)
        rimg.write(actual)

        expected = datadir.join('reconstructed.fits').strpath

        assert compare_fits(expected, actual)
        assert np.array_equal(image, rimg.img)
        assert image is not rimg.img

    def test_pscale_setter(self, datadir, tmpdir, ifucenter_file):
        dl = datadir.join(dist_l).strpath
        dr = datadir.join(dist_r).strpath

        rimg = rifu.QuickReconstructedIFU(ifucenter_file.strpath, dist_r=dr,
                                          dist_l=dl)
        rimg.pscale = 0.25

    @pytest.mark.xfail(raises=rifu.ReconstructError,
                       reason='No reconstrution happened')
    def test_write_error(self, datadir, tmpdir, ifucenter_file):
        dl = datadir.join(dist_l).strpath
        dr = datadir.join(dist_r).strpath

        rimg = rifu.QuickReconstructedIFU(ifucenter_file.strpath, dist_r=dr,
                                          dist_l=dl)

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
    def test_no_dist(self, datadir, tmpdir, ifucenter_file):

        rifu.QuickReconstructedIFU(ifucenter_file.strpath)

    def test_left_dist(self, datadir, tmpdir, ifucenter_file):
        dl = datadir.join(dist_l).strpath

        rifu.QuickReconstructedIFU(ifucenter_file.strpath, dist_l=dl)

    def test_right_dist(self, datadir, tmpdir, ifucenter_file):
        dr = datadir.join(dist_r).strpath

        rifu.QuickReconstructedIFU(ifucenter_file.strpath,
                                   dist_r=dr)

    @pytest.mark.xfail(raises=rifu.ReconstructValueError,
                       reason='Wrong distortion for the input files')
    def test_missing_dist(self, datadir, tmpdir, ifucenter_file):
        ''' Test combination of left spectrograph images with right
        spectrograph distortion
        '''
        infiles = [datadir.join(i).strpath for i in inputfilenames_l]
        dr = datadir.join(dist_r).strpath

        rimg = rifu.QuickReconstructedIFU(ifucenter_file.strpath, dist_r=dr)
        rimg.reconstruct(infiles)

    def test_wrong_ifu(self, datadir, tmpdir, ifucenter_file):
        ''' Test combination of left spectrograph images with right
        spectrograph distortion
        '''
        filenames = ['20151025T122555_104LL_sci.fits',
                     '20151025T122555_103LU_sci.fits']
        infiles = [datadir.join(i).strpath for i in filenames]
        dl = datadir.join(dist_l).strpath

        rimg = rifu.QuickReconstructedIFU(ifucenter_file.strpath,
                                          dist_l=dl)
        rimg.reconstruct(infiles)

    def test_no_overscan(self, datadir, tmpdir, ifucenter_file):
        '''Test reconstruction without overscan subtraction'''
        infiles = [datadir.join(i).strpath for i in inputfilenames_r]

        dr = datadir.join(dist_r).strpath

        rimg = rifu.QuickReconstructedIFU(ifucenter_file.strpath,
                                          dist_r=dr)
        rimg.reconstruct(infiles, subtract_overscan=False)

    def test_combined_img(self, datadir, tmpdir, ifucenter_file):
        '''Test reconstruction without overscan subtraction '''
        infile = [datadir.join('masterarc_080R.fits').strpath]
        dr = datadir.join(dist_r).strpath

        rimg = rifu.QuickReconstructedIFU(ifucenter_file.strpath,
                                          dist_r=dr)

        rimg.reconstruct(infile, subtract_overscan=False)

    def test_wrong_dither_number(self, tmpdir, clear_tmpdir, datadir,
                                 compare_fits, ifucenter_file):
        '''If the dither number is not 1, 2, 3 set it to the first one'''
        infiles = [datadir.join(i).strpath for i in inputfilenames]
        tmpfiles = [tmpdir.join(i).strpath for i in inputfilenames]
        dl = datadir.join(dist_l).strpath
        dr = datadir.join(dist_r).strpath
        # copy the input files to tmpdir changing or removing the dither header
        # keyword
        for i, (ifile, tfile) in enumerate(zip(infiles, tmpfiles)):
            with fits.open(ifile, memmap=False) as f:
                if i % 2 == 0:
                    f[0].header['DITHER'] = -99999
                else:
                    f[0].header.remove('DITHER')
                f.writeto(tfile)

        rimg = rifu.QuickReconstructedIFU(ifucenter_file.strpath, dist_r=dr,
                                          dist_l=dl)

        actual = tmpdir.join('qrecon.fits').strpath

        rimg.reconstruct(tmpfiles)
        rimg.write(actual)

        expected = datadir.join('reconstructed.fits').strpath

        assert compare_fits(expected, actual)

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

    def test_entry_point(self, datadir, tmpdir, ifucenter_file, compare_fits):
        "Quick Reconstruction from existing ifu center and dither objects"

        infiles = [datadir.join(i).strpath for i in inputfilenames]
        dl = datadir.join(dist_l).strpath
        dr = datadir.join(dist_r).strpath
        actual = tmpdir.join('qrecon.fits').strpath

        argv = ['-s', '0.25', '-l', dl, '-r', dr, '-o', actual,
                ifucenter_file.strpath]
        argv.extend(infiles)

        rifu.create_quick_reconstruction(argv)

        expected = datadir.join('reconstructed.fits').strpath

        assert compare_fits(expected, actual)
