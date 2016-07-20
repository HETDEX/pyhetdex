'''Test the module pyhetdex.het.telescope'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import random
import subprocess as sp
import stat

from astropy.io import fits
import pytest

import pyhetdex.het.telescope as tel
from pyhetdex.tools.six_ext import SubprocessExeError

parametrize = pytest.mark.parametrize


def test_shot_defaults():
    '''Test the Shot object using the default constant models'''
    def_fwhm = 1
    def_ill = 2
    def_trans = 4
    shot = tel.Shot(fwhm_fallback=def_fwhm, illumination_fallback=def_ill,
                    transparency_fallback=def_trans)

    assert isinstance(shot.fwhm_model, tel.ConstantModel)
    assert isinstance(shot.illumination_model, tel.ConstantModel)
    assert isinstance(shot.transparency_model, tel.ConstantModel)

    assert shot.fwhm(0, 0, 0) == def_fwhm
    assert shot.illumination(1, 1, 1) == def_ill
    assert shot.transparency(2) == def_trans
    assert shot.normalisation(3, 3, 3) == def_ill * def_trans


@parametrize('property_',
             ['fwhm_model', 'illumination_model', 'transparency_model'])
def test_shot_properties(property_):
    '''Test plugging and removing models'''
    class TestModel(tel.ModelInterface):
        '''Test model to test the assignment and deletion of properties'''
        def __call__(self, x, y, dither):
            pass

    shot = tel.Shot()

    assert isinstance(getattr(shot, property_), tel.ConstantModel)
    # plug the new model
    setattr(shot, property_, TestModel())
    assert isinstance(getattr(shot, property_), TestModel)
    # remove the model
    delattr(shot, property_)
    assert isinstance(getattr(shot, property_), tel.ConstantModel)


def test_constant_model():
    '''Test the constant model'''
    const = 42
    model = tel.ConstantModel(const)

    assert model(random.random(), random.random(),
                 random.randint(1, 10)) == const


@pytest.mark.xfail(raises=SubprocessExeError,
                   reason='no executable found')
def test_hetpupil_model_no_exec(monkeypatch):
    '''Non hetpupil found on the system'''
    monkeypatch.delenv('CUREBIN', raising=False)
    monkeypatch.setenv('PATH', '')

    tel.HetpupilModel([])


@parametrize('envvar', ['CUREBIN', 'PATH'])
@pytest.mark.xfail(raises=sp.CalledProcessError,
                   reason='Executable raises an error')
def test_hetpupil_model_tmpexec(tmpdir, monkeypatch, envvar):
    '''create a fake hetpupil that exit with 1 in tmpdir and add tmpdir in
    ``envvar`` after clearing up CUREBIN and PATH``'''
    hetpupil = tmpdir.join('hetpupil')
    hetpupil.write('#!/bin/bash\nexit 1')
    hetpupil.chmod(stat.S_IXUSR)
    monkeypatch.setenv('CUREBIN', '')
    monkeypatch.setenv('PATH', '')

    monkeypatch.setenv(envvar, tmpdir.strpath)

    tel.HetpupilModel([])


@parametrize('normalize', [True, False])
def test_hetpupil_model(tmpdir, skip_if_no_executable, normalize):
    '''Create two fits files into tmpdir with all the needed header entries and
    test the model'''
    skip_if_no_executable('hetpupil')
    # create the mock fits files
    fits1 = tmpdir.join('file1_L.fits').strpath
    fits2 = tmpdir.join('file2_L.fits').strpath

    hdu = fits.PrimaryHDU()
    hdu.header['STRUCTAZ'] = 320.681062

    hdu.header['TELDEC'] = '+53:03:50.2'
    hdu.header['X_STRT'] = 313.933159
    hdu.header['Y_STRT'] = -614.756816
    hdu.header['EXPTIME'] = 365.499376128
    hdu.writeto(fits1)

    hdu.header['TELDEC'] = '+53:03:53.5'
    hdu.header['X_STRT'] = 255.986771
    hdu.header['Y_STRT'] = -507.732814
    hdu.header['EXPTIME'] = 364.900277248
    hdu.writeto(fits2)

    # expected fill factors
    fill1 = 0.87
    fill2 = 0.91
    if normalize:
        fill2 /= fill1
        fill1 = 1.

    model = tel.HetpupilModel([fits1, fits2], normalize=normalize)

    assert model(0, 0, 1) == fill1
    assert model(0, 0, 2) == fill2
