from __future__ import absolute_import, print_function

import pyhetdex.ltl.marray as ma
from pyhetdex.tools import io_helpers

import numpy as np
import locale

__version__ = '$Id$'


class DistortionBase(object):

    def __init__(self, filename):

        _vdict = {14: Distortion_14,
                  17: Distortion_14}

        in_ = open(filename)
        fileversion = locale.atoi(io_helpers.skip_commentlines(in_))
        in_.close()

        if fileversion not in _vdict:
            raise IOError('Unsupported version of Distortion file!')

        self._cls = _vdict[fileversion](filename)


class Distortion(DistortionBase):

    def __init__(self, filename):
        super(Distortion, self).__init__(filename)

        self._cls.read()

    def __getattribute__(self, a):
        try:
            return super(Distortion, self).__getattribute__(a)
        except AttributeError:
            return self._cls.__getattribute__(a)

    def __setattr__(self, a, v):
        try:
            return super(Distortion, self).__setattr__(a, v)
        except AttributeError:
            return self._cls.__setattr__(a, v)


class Distortion_14(object):

    def __init__(self, filename):

        self.filename = filename
        self.version = 0
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

    def read(self):

        in_ = open(self.filename)
        self.version = locale.atoi(io_helpers.skip_commentlines(in_))
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
        self.reference_wavelength_ = locale.atof(io_helpers.skip_commentlines(in_))
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

        return self.interp(self._scal_x(x), self._scal_f(f),
                           self.fy_par_.data)

    def map_wf_x(self, w, f):

        if isinstance(w, (tuple, list)):
            w = np.asarray(w)
        if isinstance(f, (tuple, list)):
            f = np.asarray(f)

        value = self.interp(self._scal_w(w), self._scal_f(f),
                            self.x_par_.data)

        if self.reference_wavelength_ < 0:
            return value

        return value - \
            self.x_offsets_.data[self._find_closest_index(self.reference_f_.data,
                                                          f)]

    def map_wf_y(self, w, f):

        if isinstance(w, (tuple, list)):
            w = np.asarray(w)
        if isinstance(f, (tuple, list)):
            f = np.asarray(f)

        return self.interp(self._scal_w(w), self._scal_f(f),
                           self.y_par_.data)

    def map_xy_fiber(self, x, y):

        if isinstance(x, (tuple, list)):
            x = np.asarray(x)
        if isinstance(y, (tuple, list)):
            y = np.asarray(y)

        return self.interp(self._scal_x(x), self._scal_y(y),
                           self.fiber_par_.data)

    def map_xy_wavelength(self, x, y):

        if isinstance(x, (tuple, list)):
            x = np.asarray(x)
        if isinstance(y, (tuple, list)):
            y = np.asarray(y)

        value = self.interp(self._scal_x(x), self._scal_y(y),
                            self.wave_par_.data)

        if self.reference_wavelength_ < 0:
            return value

        fiber = self.map_xy_fiber(x, y)

        return value - \
            self.wave_offsets_.data[self._find_closest_index(self.reference_f_.data,
                                                             fiber)]

    def map_xy_wf(self, x, y):

        if isinstance(x, (tuple, list)):
            x = np.asarray(x)
        if isinstance(y, (tuple, list)):
            y = np.asarray(y)

        value = self.interp(self._scal_x(x), self._scal_y(y),
                            self.wave_par_.data)

        if self.reference_wavelength_ < 0:
            return value

        fiber = self.map_xy_fiber(x, y)

        return value - \
            self.wave_offsets_.data[self._find_closest_index(self.reference_f_.data,
                                                             fiber)], fiber

    def _find_closest_index(self, a, v):
        return (np.abs(a-v)).argmin()

    def interp(self, x, y, par):
        return ma.interpCheby2D_7(x, y, par)
