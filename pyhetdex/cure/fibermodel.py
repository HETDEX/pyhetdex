# Misc python library to support HETDEX software and data analysis
# Copyright (C) 2015, 2016, 2017, 2018  "The HETDEX collaboration"
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pyhetdex.ltl.marray as ma
import pyhetdex.ltl.chebyshev as cheby
from pyhetdex.tools import io_helpers
from pyhetdex.cure.gaussian import gauss1D_H
from pyhetdex.cure.bspline import BSpline

import numpy as np

__version__ = '$Id'


class FiberModelBase(object):

    def __init__(self, filename):

        _vdict = {16: FiberModel_16,
                  17: FiberModel_16,
                  18: FiberModel_18,
                  19: FiberModel_19,
                  21: FiberModel_21,
                  22: FiberModel_22}

        with open(filename) as in_:
            fileversion = int(io_helpers.skip_commentlines(in_))

        if fileversion not in _vdict:
            raise IOError('Unsupported version of Fibermodel file!')

        self._cls = _vdict[fileversion](filename)


class FiberModel(FiberModelBase):

    def __init__(self, filename):
        super(FiberModel, self).__init__(filename)

        self._cls.read()

    def __getattribute__(self, a):
        try:
            return super(FiberModel, self).__getattribute__(a)
        except AttributeError:
            return self._cls.__getattribute__(a)

    def __setattr__(self, a, v):
        try:
            return super(FiberModel, self).__setattr__(a, v)
        except AttributeError:  # pragma: no cover
            return self._cls.__setattr__(a, v)


class FiberModel_16(object):

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
        self.fiducial_fib_ = 0
        self.sigma_par_ = ma.FVector()
        self.sigma_errors_ = ma.FVector()
        self.h2_par_ = ma.FVector()
        self.h2_errors_ = ma.FVector()
        self.h3_par_ = ma.FVector()
        self.h3_errors_ = ma.FVector()
        self.amplitudes = []

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

            self.fiducial_fib_ = int(io_helpers.skip_commentlines(in_))
            self.sigma_par_.read(in_)
            self.sigma_errors_.read(in_)
            self.h2_par_.read(in_)
            self.h2_errors_.read(in_)
            self.h3_par_.read(in_)
            self.h3_errors_.read(in_)
            size = float(io_helpers.skip_commentlines(in_))
            i = 0
            while i < size:
                amp = ma.FVector()
                amp.read(in_)
                self.amplitudes.append(amp)
                i += 1


class FiberModel_18(object):

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
        self.sigma_par_ = ma.FVector()
        self.sigma_errors_ = ma.FVector()
        self.h2_par_ = ma.FVector()
        self.h2_errors_ = ma.FVector()
        self.h3_par_ = ma.FVector()
        self.h3_errors_ = ma.FVector()
        self.amplitudes = []

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

            self.sigma_par_.read(in_)
            self.sigma_errors_.read(in_)
            self.h2_par_.read(in_)
            self.h2_errors_.read(in_)
            self.h3_par_.read(in_)
            self.h3_errors_.read(in_)
            size = float(io_helpers.skip_commentlines(in_))
            i = 0
            while i < size:
                amp = ma.FVector()
                amp.read(in_)
                self.amplitudes.append(amp)
                i += 1


class FiberModel_19(object):

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
        self.sigma_par_ = ma.FVector()
        self.sigma_errors_ = ma.FVector()
        self.h2_par_ = ma.FVector()
        self.h2_errors_ = ma.FVector()
        self.h3_par_ = ma.FVector()
        self.h3_errors_ = ma.FVector()
        self.exp_par_ = ma.FVector()
        self.exp_errors_ = ma.FVector()
        self.amplitudes = []

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

            self.sigma_par_.read(in_)
            self.sigma_errors_.read(in_)
            self.h2_par_.read(in_)
            self.h2_errors_.read(in_)
            self.h3_par_.read(in_)
            self.h3_errors_.read(in_)
            self.exp_par_.read(in_)
            self.exp_errors_.read(in_)
            size = float(io_helpers.skip_commentlines(in_))
            i = 0
            while i < size:
                amp = ma.FVector()
                amp.read(in_)
                self.amplitudes.append(amp)
                i += 1


class FiberModel_21(object):

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
        self.sigma_par_ = ma.FVector()
        self.sigma_errors_ = ma.FVector()
        self.h2_par_ = ma.FVector()
        self.h2_errors_ = ma.FVector()
        self.h3_par_ = ma.FVector()
        self.h3_errors_ = ma.FVector()
        self.powerlaw_wings = []
        self.exp_par_ = ma.FVector()
        self.exp_errors_ = ma.FVector()
        self.amplitudes = []

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

            self.sigma_par_.read(in_)
            self.sigma_errors_.read(in_)
            self.h2_par_.read(in_)
            self.h2_errors_.read(in_)
            self.h3_par_.read(in_)
            self.h3_errors_.read(in_)
            self.exp_par_.read(in_)
            self.exp_errors_.read(in_)
            for i in range(0, 4):
                val = float(io_helpers.skip_commentlines(in_))
                self.powerlaw_wings.append(val)
            size = float(io_helpers.skip_commentlines(in_))
            i = 0
            while i < size:
                amp = ma.FVector()
                amp.read(in_)
                self.amplitudes.append(amp)
                i += 1


class FiberModel_22(object):

    def __init__(self, filename):

        self._max_fiber_dist = 14

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
        self.sigma_par_ = ma.FVector()
        self.sigma_errors_ = ma.FVector()
        self.h2_par_ = ma.FVector()
        self.h2_errors_ = ma.FVector()
        self.h3_par_ = ma.FVector()
        self.h3_errors_ = ma.FVector()
        self.powerlaw_wings = []
        self.exp_par_ = ma.FVector()
        self.exp_errors_ = ma.FVector()
        self.amplitudes = []

        self.profile = None

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

            self.sigma_par_.read(in_)
            self.sigma_errors_.read(in_)
            self.h2_par_.read(in_)
            self.h2_errors_.read(in_)
            self.h3_par_.read(in_)
            self.h3_errors_.read(in_)
            self.exp_par_.read(in_)
            self.exp_errors_.read(in_)
            for i in range(0, 4):
                val = float(io_helpers.skip_commentlines(in_))
                self.powerlaw_wings.append(val)
            size = int(io_helpers.skip_commentlines(in_))
            i = 0
            while i < size:
                amp = BSpline()
                amp.read(in_)
                self.amplitudes.append(amp)
                i += 1

        self.profile = gauss1D_H(self.powerlaw_wings)

    def get_params(self, x, y, D):
        '''
        Return the fit parameters at x,y  as a tuple:
        fiber, H2, H3, amp, y0, sigma, exp
        '''
        fiber = D.map_xy_fibernum(x, y)
        return fiber, self.get_xy_h2(x, y), \
            self.get_xy_h3(x, y), self.get_xy_amplitude(x, y, D), \
            D.map_xf_y(x, D.get_reference_f(fiber)), \
            self.get_xy_sigma(x, y), self.get_xy_exp(x, y)

    def get_single_fiberflux(self, x, y, D):
        _, H2, H3, amp, y0, sigma, exp = self.get_params(x, y, D)
        if abs(y-y0) > self._max_fiber_dist:
            return 0.0
        else:
            return self.profile.eval(y, amp, y0, sigma, H2, H3, exp)

    def get_single_fiberflux_fiber(self, x, y, fiber, D):
        f = D.get_reference_f(fiber)
        _y0 = D.map_xf_y(x, f)
        _, H2, H3, amp, y0, sigma, exp = self.get_params(x, _y0, D)
        if abs(y-y0) > self._max_fiber_dist:
            return 0.0
        else:
            return self.profile.eval(y, amp, y0, sigma, H2, H3, exp)

    def get_single_fiberprofile(self, x, y, D):
        _, H2, H3, amp, y0, sigma, exp = self.get_params(x, y, D)
        if abs(y-y0) > self._max_fiber_dist:
            return 0.0
        else:
            return self.profile.eval(y, amp, y0, sigma, H2, H3, exp) / \
                self.profile.eval(y0, amp, y0, sigma, H2, H3, exp)

    def get_single_fiberprofile_fiber(self, x, y, fiber, D):
        f = D.get_reference_f(fiber)
        _y0 = D.map_xf_y(x, f)
        _, H2, H3, amp, y0, sigma, exp = self.get_params(x, _y0, D)
        if abs(y-y0) > self._max_fiber_dist:
            return 0.0
        else:
            return self.profile.eval(y, amp, y0, sigma, H2, H3, exp) / \
                self.profile.eval(y0, amp, y0, sigma, H2, H3, exp)

    def get_cumulative_fiberflux(self, x, y, D):
        fiber = D.map_xy_fibernum(x, y)
        f = self.get_single_fiberflux(x, y, D)

        if fiber > 1:
            f += self.get_single_fiberflux_fiber(x, y, fiber-1, D)

        if fiber < D.get_numfibers():
            f += self.get_single_fiberflux_fiber(x, y, fiber+1, D)

        return f

    def get_xy_amplitude(self, x, y, D):
        return self.get_wf_amplitude(D.map_xy_wavelength(x, y),
                                     D.map_xy_fibernum(x, y))

    def get_wf_amplitude(self, w, f):
        return self.amplitudes[int(f)-1].evaluate(self._scal_w(w))

    def get_xy_sigma(self, x, y):
        return self.interp(self._scal_x(x), self._scal_y(y),
                           self.sigma_par_.data)

    def get_xy_h2(self, x, y):
        return self.interp(self._scal_x(x), self._scal_y(y), self.h2_par_.data)

    def get_xy_h3(self, x, y):
        return self.interp(self._scal_x(x), self._scal_y(y), self.h3_par_.data)

    def get_xy_exp(self, x, y):
        return self.interp(self._scal_x(x), self._scal_y(y),
                           self.exp_par_.data)

    def _scal_x(self, x):
        return (x - self.minx) / (self.maxx - self.minx)

    def _scal_y(self, y):
        return (y - self.miny) / (self.maxy - self.miny)

    def _scal_w(self, w):
        return (w - self.minw) / (self.maxw - self.minw)

    def interp(self, x, y, par):
        return cheby.interpCheby2D_7(x, y, par)


class InterpolatedFiberModel(object):

    def __init__(self, filename):

        self.filename = filename
        self.version = 0
        self._profile = None
        self._map = None

    def read(self):

        from astropy.io import fits
        hdu = fits.open(self.filename)
        self._profile = hdu['MODEL']
        self._map = hdu['MAP']

    def get_single_fiberflux(self, x, y, D):
        x0 = int(floor(x))
        fib = D.map_xy_fibernum(x, y)
        ref_f = D.get_reference_f(fib)
        ref_y = D.map_xf_y(x, ref_f)
        prof_y = y - ref_y

        return np.interp(prof_y, self._map, self._profile[fib, :, x])

    def get_single_fiberflux_fiber(self, x, y, fiber, D):
        f = D.get_reference_f(fiber)
        _y0 = D.map_xf_y(x, f)
        _, H2, H3, amp, y0, sigma, exp = self.get_params(x, _y0, D)
        if abs(y-y0) > self._max_fiber_dist:
            return 0.0
        else:
            return self.profile.eval(y, amp, y0, sigma, H2, H3, exp)

    def get_single_fiberprofile(self, x, y, D):
        _, H2, H3, amp, y0, sigma, exp = self.get_params(x, y, D)
        if abs(y-y0) > self._max_fiber_dist:
            return 0.0
        else:
            return self.profile.eval(y, amp, y0, sigma, H2, H3, exp) / \
                self.profile.eval(y0, amp, y0, sigma, H2, H3, exp)

    def get_single_fiberprofile_fiber(self, x, y, fiber, D):
        f = D.get_reference_f(fiber)
        _y0 = D.map_xf_y(x, f)
        _, H2, H3, amp, y0, sigma, exp = self.get_params(x, _y0, D)
        if abs(y-y0) > self._max_fiber_dist:
            return 0.0
        else:
            return self.profile.eval(y, amp, y0, sigma, H2, H3, exp) / \
                self.profile.eval(y0, amp, y0, sigma, H2, H3, exp)

    def get_cumulative_fiberflux(self, x, y, D):
        fiber = D.map_xy_fibernum(x, y)
        f = self.get_single_fiberflux(x, y, D)

        if fiber > 1:
            f += self.get_single_fiberflux_fiber(x, y, fiber-1, D)

        if fiber < D.get_numfibers():
            f += self.get_single_fiberflux_fiber(x, y, fiber+1, D)

        return f

    def get_xy_amplitude(self, x, y, D):
        return self.get_wf_amplitude(D.map_xy_wavelength(x, y),
                                     D.map_xy_fibernum(x, y))

    def get_wf_amplitude(self, w, f):
        return self.amplitudes[int(f)-1].evaluate(self._scal_w(w))

    def get_xy_sigma(self, x, y):
        return self.interp(self._scal_x(x), self._scal_y(y),
                           self.sigma_par_.data)

    def get_xy_h2(self, x, y):
        return self.interp(self._scal_x(x), self._scal_y(y), self.h2_par_.data)

    def get_xy_h3(self, x, y):
        return self.interp(self._scal_x(x), self._scal_y(y), self.h3_par_.data)

    def get_xy_exp(self, x, y):
        return self.interp(self._scal_x(x), self._scal_y(y),
                           self.exp_par_.data)

    def _scal_x(self, x):
        return (x - self.minx) / (self.maxx - self.minx)

    def _scal_y(self, y):
        return (y - self.miny) / (self.maxy - self.miny)

    def _scal_w(self, w):
        return (w - self.minw) / (self.maxw - self.minw)

    def interp(self, x, y, par):
        return cheby.interpCheby2D_7(x, y, par)
