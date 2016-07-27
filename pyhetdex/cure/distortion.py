from __future__ import absolute_import, print_function

import pyhetdex.ltl.marray as ma
from pyhetdex.tools import io_helpers

import datetime
import numpy as np

__version__ = '$Id$'


class DistortionBase(object):

    def __init__(self, filename):

        _vdict = {14: Distortion_14,
                  17: Distortion_14}

        in_ = open(filename)
        fileversion = int(io_helpers.skip_commentlines(in_))
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
        except AttributeError:  # pragma: no cover
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

        with open(self.filename) as in_:
            self.version = int(io_helpers.skip_commentlines(in_))
            self.minw = float(io_helpers.skip_commentlines(in_))
            self.maxw = float(io_helpers.skip_commentlines(in_))
            self.minf = float(io_helpers.skip_commentlines(in_))
            self.maxf = float(io_helpers.skip_commentlines(in_))
            self.minx = float(io_helpers.skip_commentlines(in_))
            self.maxx = float(io_helpers.skip_commentlines(in_))
            self.miny = float(io_helpers.skip_commentlines(in_))
            self.maxy = float(io_helpers.skip_commentlines(in_))

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
            self.reference_wavelength_ = \
                float(io_helpers.skip_commentlines(in_))
            self.reference_w_.read(in_)
            self.reference_f_.read(in_)
            self.wave_offsets_.read(in_)
            self.x_offsets_.read(in_)

    def writeto(self, filename):
        with open(filename, 'w') as out_:
            out_.write('# CALL : Written by pyhetdex %s\n' % __version__)
            out_.write('#FILE CREATED ON : %s\n'
                       % datetime.datetime.now().strftime('%c'))
            out_.write('# Title: Distortion model\n')
            out_.write('%d\n' % self.version)
            out_.write('%.6e\n' % self.minw)
            out_.write('%.6e\n' % self.maxw)
            out_.write('%.6e\n' % self.minf)
            out_.write('%.6e\n' % self.maxf)
            out_.write('%.6e\n' % self.minx)
            out_.write('%.6e\n' % self.maxx)
            out_.write('%.6e\n' % self.miny)
            out_.write('%.6e\n' % self.maxy)
            self.wave_par_.write(out_)
            self.wave_errors_.write(out_)
            self.fiber_par_.write(out_)
            self.fiber_errors_.write(out_)
            self.x_par_.write(out_)
            self.x_errors_.write(out_)
            self.y_par_.write(out_)
            self.y_errors_.write(out_)
            self.fy_par_.write(out_)
            self.fy_errors_.write(out_)
            out_.write('%.6e\n' % self.reference_wavelength_)
            self.reference_w_.write(out_)
            self.reference_f_.write(out_)
            self.wave_offsets_.write(out_)
            self.x_offsets_.write(out_)

    def _scal_x(self, x):
        return (x - self.minx) / (self.maxx - self.minx)

    def _scal_y(self, y):
        return (y - self.miny) / (self.maxy - self.miny)

    def _scal_w(self, w):
        return (w - self.minw) / (self.maxw - self.minw)

    def _scal_f(self, f):
        return (f - self.minf) / (self.maxf - self.minf)

    def get_numfibers(self):
        return len(self.reference_f_.data)

    def get_reference_f(self, fiber):
        return self.reference_f_.data[fiber-1]

    def map_xy_fiber(self, x, y):

        if isinstance(x, (tuple, list)):
            x = np.asarray(x)
        if isinstance(y, (tuple, list)):
            y = np.asarray(y)

        return self.interp(self._scal_x(x), self._scal_y(y),
                           self.fiber_par_.data)

    def map_xy_wavelength(self, x, y):

        w, f = self.map_xy_wf(x, y)
        return w

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

        if np.isscalar(fiber):
            return value-self.wave_offsets_.data[self._closest_fiber(fiber)], \
                fiber

        wo = [self.wave_offsets_.data[self._closest_fiber(fib)]
              for fib in fiber]
        return value-np.array(wo), fiber

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

        if np.isscalar(f):
            return value-self.x_offsets_.data[self._closest_fiber(f)]

        xo = [self.x_offsets_.data[self._closest_fiber(fib)] for fib in f]
        return value - np.array(xo)

    def map_wf_y(self, w, f):

        if isinstance(w, (tuple, list)):
            w = np.asarray(w)
        if isinstance(f, (tuple, list)):
            f = np.asarray(f)

        return self.interp(self._scal_w(w), self._scal_f(f),
                           self.y_par_.data)

    def map_xy_fibernum(self, x, y):
        f = self.map_xy_fiber(x, y)
        # Fibernumbers are one based, numpy arrays zero based
        return self._closest_fiber(f) + 1

    def _closest_fiber(self, f):
        if np.isscalar(f):
            return self._find_closest_index(self.reference_f_.data, f)

        idx = [self._find_closest_index(self.reference_f_.data, fib)
               for fib in f]
        return np.array(idx)

    def _find_closest_index(self, a, v):
        return (np.abs(a-v)).argmin()

    def interp(self, x, y, par):
        return ma.interpCheby2D_7(x, y, par)
