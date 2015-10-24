from __future__ import absolute_import, print_function

__version__ = '$Id'

from pyhetdex.ltl.MArray import MArray, FVector
from pyhetdex.tools import io_helpers

import locale

class FiberModel(object):
    
    def __init__(self, filename):
        
        self.filename=''

        self.version=0
        self.version_min=16
        self.version_max=16
        self.minw=float(0)
        self.maxw=float(0)
        self.minf=float(0)
        self.maxf=float(0)
        self.minx=float(0)
        self.maxx=float(0)
        self.miny=float(0)
        self.maxy=float(0)
        self.fiducial_fib_=0
        self.sigma_par_ = FVector(dtype='double')
        self.sigma_errors_ = FVector(dtype='double')
        self.h2_par_ = FVector(dtype='double')
        self.h2_errors_ = FVector(dtype='double')
        self.h3_par_ = FVector(dtype='double')
        self.h3_errors_ = FVector(dtype='double')
        self.amplitudes=[]
  
        self.read(filename)
        
    def read(self,filename):

        self.filename = filename
                
        in_=open( self.filename )
        fileversion=locale.atoi(io_helpers.skip_commentlines(in_))
        if( fileversion < self.version_min or fileversion > self.version_max ):
            raise IOError( 'Unsupported version of FiberModel file!')        
        self.minw=locale.atof(io_helpers.skip_commentlines(in_))
        self.maxw=locale.atof(io_helpers.skip_commentlines(in_))
        self.minf=locale.atof(io_helpers.skip_commentlines(in_))
        self.maxf=locale.atof(io_helpers.skip_commentlines(in_))
        self.minx=locale.atof(io_helpers.skip_commentlines(in_))
        self.maxx=locale.atof(io_helpers.skip_commentlines(in_))
        self.miny=locale.atof(io_helpers.skip_commentlines(in_))
        self.maxy=locale.atof(io_helpers.skip_commentlines(in_))

        self.fiducial_fib_=locale.atoi(io_helpers.skip_commentlines(in_))
        self.sigma_par_.read(in_)
        self.sigma_errors_.read(in_)
        self.h2_par_.read(in_)
        self.h2_errors_.read(in_)
        self.h3_par_.read(in_)
        self.h3_errors_.read(in_)
        size=locale.atof(io_helpers.skip_commentlines(in_))
        print( 'Reading %d amplitudes' % size )
        i=0
        while i<size:
            amp=FVector( dtype='double')
            amp.read(in_)
            self.amplitudes.append( amp )
            i+=1
