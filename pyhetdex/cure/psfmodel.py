from __future__ import absolute_import, print_function

__version__ = '$Id'

from pyhetdex.ltl.marray import FVector
from pyhetdex.tools import io_helpers

import locale


class PSFModelBase(object):

    def __init__(self, filename):

        _vdict = {2: PSFModel_2,
                  3: PSFModel_3}

        in_ = open(filename)
        fileversion = locale.atoi(io_helpers.skip_commentlines(in_))
        in_.close()

        if fileversion not in _vdict:
            raise IOError('Unsupported version of PSFModel file!')

        self._cls = _vdict[fileversion](filename)


class PSFModel(PSFModelBase):

    def __init__(self, filename):
        super(PSFModel, self).__init__(filename)

        self._cls.read()

    def __getattribute__(self, a):
        try:
            return super(PSFModel, self).__getattribute__(a)
        except AttributeError:
            return self._cls.__getattribute__(a)

    def __setattr__(self, a, v):
        try:
            return super(PSFModel, self).__setattr__(a, v)
        except AttributeError:
            return self._cls.__setattr__(a, v)


class PSFModel_2(object):

    def __init__(self, filename):

        self.filename = filename
        self.version = 0
        self.minx = float(0)
        self.maxx = float(0)
        self.miny = float(0)
        self.maxy = float(0)
        self.sigx_par_ = FVector()
        self.sigy_par_ = FVector()
        self.h2y_par_ = FVector()
        self.h3y_par_ = FVector()

    def read(self):

        in_ = open(self.filename)
        self.version = locale.atoi(io_helpers.skip_commentlines(in_))
        self.minx = locale.atof(io_helpers.skip_commentlines(in_))
        self.maxx = locale.atof(io_helpers.skip_commentlines(in_))
        self.miny = locale.atof(io_helpers.skip_commentlines(in_))
        self.maxy = locale.atof(io_helpers.skip_commentlines(in_))

        self.sigx_par_.read(in_)
        self.sigy_par_.read(in_)
        self.h2y_par_.read(in_)
        self.h3y_par_.read(in_)


class PSFModel_3(PSFModel_2):

    def __init__(self, filename):

        super(PSFModel_3, self).__init__(filename)

        # Add new parameters
        self.minw = float(0)
        self.maxw = float(0)
        self.minf = float(0)
        self.maxf = float(0)

    def read(self):

        # Overload the complete read routine
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

        self.sigx_par_.read(in_)
        self.sigy_par_.read(in_)
        self.h2y_par_.read(in_)
        self.h3y_par_.read(in_)
