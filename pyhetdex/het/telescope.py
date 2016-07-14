""" Telescope module

Stores information related to the guide, i.e. guide probe and tracker
information. Also deals with illumination and image quality servers.

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import abc
from distutils.spawn import find_executable
import os
import subprocess as sp

import numpy as np
from pyhetdex.tools.six_ext import SubprocessExeError
import six


class Shot(object):
    """Class to store information about the whole shot and retrieve fwhm,
    illumination, transparency and normalization.

    Each of them rely on some underlying model, with the interface defined by
    :class:`ModelInterface`

    Parameters
    ----------
    fwhm_fallback : float, optionally
        number to use when instantiating a :class:`ConstantModel` if a
        :attr:`fwhm_model` is not provided
    illumination_fallback : float, optionally
        number to use when instantiating a :class:`ConstantModel` if a
        :attr:`illumination_model` is not provided
    transparency_fallback : float, optionally
        number to use when instantiating a :class:`ConstantModel` if a
        :attr:`transparency_model` is not provided

    Attributes
    ----------
    fwhm_model
    illumination_model
    transparency_model
    """
    def __init__(self, fwhm_fallback=1.6, illumination_fallback=1.,
                 transparency_fallback=1.):
        self._fwhm = None
        self._illumination = None
        self._transparency = None
        self._fwhm_fallback = fwhm_fallback
        self._illumination_fallback = illumination_fallback
        self._transparency_fallback = transparency_fallback

    @property
    def fwhm_model(self):
        '''Retrieve, set or remove the fwhm model. If not set or removed, fall
        back to one that returns a constant value'''
        if self._fwhm is None:
            self._fwhm = ConstantModel(self._fwhm_fallback)
        return self._fwhm

    @fwhm_model.setter
    def fwhm_model(self, model):
        self._fwhm = model

    @fwhm_model.deleter
    def fwhm_model(self):
        self._fwhm = None

    def fwhm(self, x, y, dither):
        """ Return the FWHM

        Parameters
        ----------
        x, y : float
            position in the focal plane in arcseconds
        dither : int
            the dither number
        """
        return self.fwhm_model(x, y, dither)

    @property
    def illumination_model(self):
        '''Retrieve, set or remove the illumination model. If not set or removed, fall
        back to one that returns a constant value'''
        if self._illumination is None:
            self._illumination = ConstantModel(self._illumination_fallback)
        return self._illumination

    @illumination_model.setter
    def illumination_model(self, model):
        self._illumination = model

    @illumination_model.deleter
    def illumination_model(self):
        self._illumination = None

    def illumination(self, x, y, dither):
        """ Return the illumination

        Parameters
        ----------
        x,y : float
            position in the focal plane in arcseconds
        dither : int
            the dither number
        """
        return self.illumination_model(x, y, dither)

    @property
    def transparency_model(self):
        '''Retrieve, set or remove the transparency model. If not set or removed, fall
        back to one that returns a constant value'''
        if self._transparency is None:
            self._transparency = ConstantModel(self._transparency_fallback)
        return self._transparency

    @transparency_model.setter
    def transparency_model(self, model):
        self._transparency = model

    @transparency_model.deleter
    def transparency_model(self):
        self._transparency = None

    def transparency(self, dither):
        """ Return the sky transparency

        Parameters
        ----------
        dither : int
            the dither number
        """
        return self.transparency_model(0, 0, dither)

    def normalisation(self, x, y, dither):
        """ Return the normalisation (transparency * illumination)

        Parameters
        ----------
        x, y : float
            position in the focal plane in arcseconds
        dither : int
            the dither number
        """
        return (self.illumination(x, y, dither) *
                self.transparency(dither))


# ==== Models ====

@six.add_metaclass(abc.ABCMeta)
class ModelInterface(object):
    '''Abstract Base Class for the models. :class:`Shot` expects that all the
    models are derived from this one and/or that implement the
    :meth:`__call__`'''
    @abc.abstractmethod
    def __call__(self, x, y, dither):  # pragma: no cover
        '''Returns the value of the model in position x, y for ``dither``

        Parameters
        ----------
        x, y : float
            position in the focal plane in arcseconds
        dither : int
            the dither number, it should start from 1

        Returns
        -------
        number
            value of the model
        '''
        pass


class ConstantModel(ModelInterface):
    '''Dummy model that always return the value passed to the constructor

    Parameters
    ----------
    constant : number
        number that :meth:`__call__` should return
    '''
    def __init__(self, constant):
        self._constant = constant

    def __call__(self, x, y, dither):
        '''Returns the constant passed to the constructor. The arguments are
        ignored'''
        return self._constant


class HetpupilModel(ModelInterface):
    '''Run the ``$CUREBIN/hetpupil`` code on the input files and save the
    relative illumination into a list. If required normalize the whole list to
    the first element. :func:`subprocess.check_output` is used.

    ``hetpupil`` is searched in CUREBIN and then in the path

    Parameters
    ----------
    files : list of strings
        name of the files on which to run the command
    normalize : bool, optional
        normalize the output of hetpupil to the first value found

    Attributes
    ----------
    fill_factor : list
        list of filling factors for each input file

    Raises
    ------
    ``pyhetdex.tools.six_ext.SubprocessExeError``
        if he hetpupil executable cannot be found
    '''
    def __init__(self, files, normalize=True):
        # try to get distutils from the path
        hetpupil = find_executable('hetpupil',
                                   path=os.environ.get('CUREBIN', None))
        if not hetpupil:  # otherwise in CUREBIN
            hetpupil = find_executable('hetpupil')

        if not hetpupil:
            raise SubprocessExeError('The executable ``hetpupil`` cannot be'
                                     ' found in $CUREBIN nor in the $PATH')

        cmd_list = [hetpupil, '-q'] + files
        stdout = sp.check_output(cmd_list, universal_newlines=True)

        self.fill_factor = [float(i.split()[-1].strip())
                            for i in stdout.splitlines()]
        self.fill_factor = np.array(self.fill_factor)
        if normalize:
            self.fill_factor /= self.fill_factor[0]

    def __call__(self, x, y, dither):
        '''Returns the value of the model for ``dither``. ``x/y`` are ignored

        Parameters
        ----------
        x, y : float
            position in the focal plane in arcseconds
        dither : int
            the dither number, starting from 1

        Returns
        -------
        float
            relative/absolute pupil fill factor
        '''
        return self.fill_factor[dither - 1]
