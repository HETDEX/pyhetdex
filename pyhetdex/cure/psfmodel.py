from __future__ import absolute_import, print_function

__version__ = '$Id'

from pyhetdex.ltl.marray import FVector
from pyhetdex.tools import io_helpers

import locale


class PSFModel(object):

    def __init__(self, filename):

        self.filename = ''
        self.version = 0
        self.version_min = 2
        self.version_max = 2
        self.minx = float(0)
        self.maxx = float(0)
        self.miny = float(0)
        self.maxy = float(0)
        self.sigx_par_ = FVector()
        self.sigy_par_ = FVector()
        self.h2y_par_ = FVector()
        self.h3y_par_ = FVector()

        self.read(filename)

    def read(self, filename):

        self.filename = filename

        in_ = open(self.filename)
        fileversion = locale.atoi(io_helpers.skip_commentlines(in_))
        if(fileversion < self.version_min or fileversion > self.version_max):
            raise IOError('Unsupported version of PSFModel file!')

        self.version = fileversion
        self.minx = locale.atof(io_helpers.skip_commentlines(in_))
        self.maxx = locale.atof(io_helpers.skip_commentlines(in_))
        self.miny = locale.atof(io_helpers.skip_commentlines(in_))
        self.maxy = locale.atof(io_helpers.skip_commentlines(in_))

        self.sigx_par_.read(in_)
        self.sigy_par_.read(in_)
        self.h2y_par_.read(in_)
        self.h3y_par_.read(in_)
