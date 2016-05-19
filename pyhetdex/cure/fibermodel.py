from __future__ import absolute_import, print_function

__version__ = '$Id'

from pyhetdex.ltl.marray import FVector
from pyhetdex.tools import io_helpers

import locale


class FiberModelBase(object):

    def __init__(self, filename):

        _vdict = {16: FiberModel_16,
                  17: FiberModel_16,
                  18: FiberModel_18,
                  19: FiberModel_19,
                  21: FiberModel_21}

        in_ = open(filename)
        fileversion = locale.atoi(io_helpers.skip_commentlines(in_))
        in_.close()

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
        except AttributeError:
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
        self.sigma_par_ = FVector()
        self.sigma_errors_ = FVector()
        self.h2_par_ = FVector()
        self.h2_errors_ = FVector()
        self.h3_par_ = FVector()
        self.h3_errors_ = FVector()
        self.amplitudes = []

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

        self.fiducial_fib_ = locale.atoi(io_helpers.skip_commentlines(in_))
        self.sigma_par_.read(in_)
        self.sigma_errors_.read(in_)
        self.h2_par_.read(in_)
        self.h2_errors_.read(in_)
        self.h3_par_.read(in_)
        self.h3_errors_.read(in_)
        size = locale.atof(io_helpers.skip_commentlines(in_))
        # print('Reading %d amplitudes' % size)
        i = 0
        while i < size:
            amp = FVector()
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
        self.sigma_par_ = FVector()
        self.sigma_errors_ = FVector()
        self.h2_par_ = FVector()
        self.h2_errors_ = FVector()
        self.h3_par_ = FVector()
        self.h3_errors_ = FVector()
        self.amplitudes = []

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

        self.sigma_par_.read(in_)
        self.sigma_errors_.read(in_)
        self.h2_par_.read(in_)
        self.h2_errors_.read(in_)
        self.h3_par_.read(in_)
        self.h3_errors_.read(in_)
        size = locale.atof(io_helpers.skip_commentlines(in_))
        # print('Reading %d amplitudes' % size)
        i = 0
        while i < size:
            amp = FVector()
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
        self.sigma_par_ = FVector()
        self.sigma_errors_ = FVector()
        self.h2_par_ = FVector()
        self.h2_errors_ = FVector()
        self.h3_par_ = FVector()
        self.h3_errors_ = FVector()
        self.exp_par_ = FVector()
        self.exp_errors_ = FVector()
        self.amplitudes = []

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

        self.sigma_par_.read(in_)
        self.sigma_errors_.read(in_)
        self.h2_par_.read(in_)
        self.h2_errors_.read(in_)
        self.h3_par_.read(in_)
        self.h3_errors_.read(in_)
        self.exp_par_.read(in_)
        self.exp_errors_.read(in_)
        size = locale.atof(io_helpers.skip_commentlines(in_))
        # print('Reading %d amplitudes' % size)
        i = 0
        while i < size:
            amp = FVector()
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
        self.sigma_par_ = FVector()
        self.sigma_errors_ = FVector()
        self.h2_par_ = FVector()
        self.h2_errors_ = FVector()
        self.h3_par_ = FVector()
        self.h3_errors_ = FVector()
        self.powerlaw_wings = []
        self.exp_par_ = FVector()
        self.exp_errors_ = FVector()
        self.amplitudes = []

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

        self.sigma_par_.read(in_)
        self.sigma_errors_.read(in_)
        self.h2_par_.read(in_)
        self.h2_errors_.read(in_)
        self.h3_par_.read(in_)
        self.h3_errors_.read(in_)
        self.exp_par_.read(in_)
        self.exp_errors_.read(in_)
        for i in range(0, 4):
            val = locale.atof(io_helpers.skip_commentlines(in_))
            self.powerlaw_wings.append(val)
        size = locale.atof(io_helpers.skip_commentlines(in_))
        # print('Reading %d amplitudes' % size)
        i = 0
        while i < size:
            amp = FVector()
            amp.read(in_)
            self.amplitudes.append(amp)
            i += 1
