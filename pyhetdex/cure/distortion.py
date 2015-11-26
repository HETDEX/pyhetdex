from __future__ import absolute_import, print_function

__version__ = '$Id$'

import pyhetdex.ltl.marray as ma
from pyhetdex.tools import io_helpers

import numpy as np

import locale


class Distortion(object):

    def __init__(self, filename):

        self.filename = ''
        self.version = 0
        self.version_min = 14
        self.version_max = 14
        self.minw = float(0)
        self.maxw = float(0)
        self.minf = float(0)
        self.maxf = float(0)
        self.minx = float(0)
        self.maxx = float(0)
        self.miny = float(0)
        self.maxy = float(0)
        self.wave_par_ = ma.FVector()
        self.wave_errors_ = ma.FVector()
        self.fiber_par_ = ma.FVector()
        self.fiber_errors_ = ma.FVector()
        self.x_par_ = ma.FVector()
        self.x_errors_ = ma.FVector()
        self.y_par_ = ma.FVector()
        self.y_errors_ = ma.FVector()
        self.fy_par_ = ma.FVector()
        self.fy_errors_ = ma.FVector()
        self.reference_wavelength_ = float(0)
        self.reference_w_ = ma.MArray()
        self.reference_f_ = ma.MArray()
        self.wave_offsets_ = ma.MArray()
        self.x_offsets_ = ma.MArray()

        self.read(filename)

    def read(self, filename):

        self.filename = filename
        in_ = open(self.filename)
        fileversion = locale.atoi(io_helpers.skip_commentlines(in_))
        if(fileversion < self.version_min or fileversion > self.version_max):
            raise IOError('Unsupported version of Distortion file!')
        self.version = fileversion
        self.minw = locale.atof(io_helpers.skip_commentlines(in_))
        self.maxw = locale.atof(io_helpers.skip_commentlines(in_))
        self.minf = locale.atof(io_helpers.skip_commentlines(in_))
        self.maxf = locale.atof(io_helpers.skip_commentlines(in_))
        self.minx = locale.atof(io_helpers.skip_commentlines(in_))
        self.maxx = locale.atof(io_helpers.skip_commentlines(in_))
        self.miny = locale.atof(io_helpers.skip_commentlines(in_))
        self.maxy = locale.atof(io_helpers.skip_commentlines(in_))

        self.wave_par_.read(in_)
        self.wave_errors_.read(in_)
        self.fiber_par_.read(in_)
        self.fiber_errors_.read(in_)
        self.x_par_.read(in_)
        self.x_errors_.read(in_)
        self.y_par_.read(in_)
        self.y_errors_.read(in_)
        self.fy_par_.read(in_)
        self.fy_errors_.read(in_)
        self.reference_wavelength = locale.atof(io_helpers.skip_commentlines(in_))
        self.reference_w_.read(in_)
        self.reference_f_.read(in_)
        self.wave_offsets_.read(in_)
        self.x_offsets_.read(in_)

    def _scal_x(self, x):
        return (x - self.minx) / (self.maxx - self.minx)

    def _scal_y(self, y):
        return (y - self.miny) / (self.maxy - self.miny)

    def _scal_w(self, w):
        return (w - self.minw) / (self.maxw - self.minw)

    def _scal_f(self, f):
        return (f - self.minf) / (self.maxf - self.minf)

    def map_xf_y(self, x, f):

        if isinstance(x, (tuple, list)):
            x = np.asarray(x)
        if isinstance(f, (tuple, list)):
            f = np.asarray(f)

        return ma.interpCheby2D_7(self._scal_x(x), self._scal_f(f),
                                  self.fy_par_.data)
