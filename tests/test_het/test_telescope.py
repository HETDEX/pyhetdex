'''Test the module pyhetdex.het.telescope'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import random

import pytest

import pyhetdex.het.telescope as tel

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
