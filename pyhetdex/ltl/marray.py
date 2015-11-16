from __future__ import absolute_import, print_function

__version__ = '$Id$'

import numpy as np
from pyhetdex.tools import io_helpers

_typedict = {'float': 'single', 'double': 'double', 'int': 'intc', 'char': 'byte'}
_formatdict = {'float': ' %.16e', 'double': ' %.16e', 'int': ' %d', 'char': ' %c'}


class FVector:
    ''' Python class allowing reading / writing of ltl/FVector object.'''

    data = None
    ftype = ''
    format = ''
    size = 0

    def __init__(self, dtype='float'):
        if dtype not in _typedict:
            raise Exception('Data format %s is not supported.' % dtype)
        self.ftype = _typedict[dtype]
        self.format = _formatdict[dtype]

    def read(self, ios):

        # First read the header, format is:
        # FVector< T,36,0 >

        dtype = io_helpers.read_to_char(ios, '<').strip()
        if (dtype != 'FVector'):
            raise Exception('Expected FVector, got %s' % dtype)

        io_helpers.eat_to_char(ios, ',')  # Forward through  < T,

        self.size = int(io_helpers.read_to_char(ios, ','))  # Read size to next ,

        stride = int(io_helpers.read_to_char(ios, '>'))
        if (stride != 0):
            raise Exception('Only stride 0 is supported')

        # Read actual data in
        # Data is in format  [ 6.4277265720642998e+00 4.6045159399542094e+01 1.7884131502943873e+02]
        # Could span several lines
        io_helpers.eat_to_blockstart(ios)  # Go to start of data

        self.data = np.fromstring(io_helpers.read_to_char(ios, ']'), dtype=self.ftype, sep=' ')

        if (self.data.size != self.size):
            raise Exception('Expected to read %d elements, got %d' % (self.size, self.data.size))

        # Clean up the trainling newline
        io_helpers.eat_to_char(ios, '\n')

    def write(self, ios):

        ios.write("FVector< T,%d,0 >\n " % self.size)
        ios.write("[")
        for i in range(0, self.size):
            ios.write(self.format % self.data[i])
            if not ((i+1) % 9):
                ios.write('\n  ')

        ios.write(" ]\n")


class MArray:
    ''' Python class allowing reading / writing of ltl/MArray object.'''

    data = None
    ftype = ''
    format = ''
    ndims = 0
    size = 0

    def __init__(self, dtype='float'):
        if dtype not in _typedict:
            raise Exception('Data format %s is not supported.' % dtype)
        self.ftype = _typedict[dtype]
        self.format = _formatdict[dtype]

    def read(self, ios):

        # First read the header, format is:
        # MArray<T,2> ( 14 x 246 ) : (1,14) (1,246)

        dtype = io_helpers.read_to_char(ios, '<').strip()
        if (dtype != 'MArray'):
            raise Exception('Expected MArray, got %s' % dtype)

        io_helpers.eat_to_char(ios, ',')  # Forward through  < T,

        self.ndims = int(io_helpers.read_to_char(ios, '>'))  # Read dimensions

        io_helpers.eat_to_char(ios, '(')  # Forward to sizes

        self.size = []

        d = 1
        while (d < self.ndims):
            self.size.append(int(io_helpers.read_to_char(ios, 'x')))
            d += 1

        self.size.append(int(io_helpers.read_to_char(ios, ')')))

        # ios.readline() # Read rest of descriptor line

        # Read actual data in
        # Data is in format  [ 6.4277265720642998e+00 4.6045159399542094e+01 1.7884131502943873e+02]
        # Could span several lines

        # Allocate data array
        self.size.reverse()
        data = np.zeros(self.size, self.ftype)
        self.size.reverse()

        # Read actual data in
        io_helpers.eat_to_blockstart(ios)

        # Now we are at the beginning of the first data block

        i = 0
        while (i < data.size):
            val = io_helpers.read_to_char(ios, ']')
            data.flat[i:i+self.size[0]] = np.fromstring(val, dtype=self.ftype, sep=' ')
            i = i+self.size[0]
            if(i < data.size):
                io_helpers.eat_to_blockstart(ios)

        self.data = data.transpose()

        # Clean up the trailing newline
        io_helpers.eat_to_char(ios, '\n')

    def write(self, ios):

        # Write header line
        dimstr = '( %d' % self.size[0]
        sizestr = '(1,%d)' % self.size[0]

        d = 1
        while (d < self.ndims):
            dimstr = dimstr + (" x %d" % self.size[d])
            sizestr = sizestr + (" (1,%d)" % self.size[d])
            d += 1
        dimstr = dimstr + " )"

        ios.write("MArray<T,%d> %s : %s\n" % (self.ndims, dimstr, sizestr))

        # Write the data

        self.__recursive_write(ios, self.data, 0, ' ')
        ios.write(']\n')

    def __recursive_write(self, ios, data, i, pad):
        ios.write('[')
        if (data.ndim > 1):
            while (i < data.shape[-1]):
                self.__recursive_write(ios, data[..., i], 0, pad+' ')
                i = i+1
                ios.write(']')
                if(i < data.shape[-1]):
                    ios.write('\n'+pad)
        else:
            for j in range(0, data.size):
                ios.write(self.format % data[j])
                if not ((j+1) % 9):
                    ios.write('\n'+pad)
            ios.write(' ')


def interpCheby2D_7(x, y, p):

    if isinstance(x, (tuple, list)):
        x = np.asarray(x)
    if isinstance(y, (tuple, list)):
        y = np.asarray(y)

    T2x = 2. * x**2 - 1.
    T3x = 4. * x**3 - 3. * x
    T4x = 8. * x**4 - 8. * x**2 + 1.
    T5x = 16. * x**5 - 20. * x**3 + 5. * x
    T6x = 32. * x**6 - 48. * x**4 + 18. * x**2 - 1.
    T7x = 64. * x**7 - 112. * x**5 + 56. * x**3 - 7. * x
    T2y = 2. * y**2 - 1.
    T3y = 4. * y**3 - 3. * y
    T4y = 8. * y**4 - 8. * y**2 + 1.
    T5y = 16. * y**5 - 20. * y**3 + 5. * y
    T6y = 32. * y**6 - 48. * y**4 + 18. * y**2 - 1
    T7y = 64. * y**7 - 112. * y**5 + 56. * y**3 - 7 * y

    return p[0]*T7x + p[1]*T6x + p[2]*T5x + p[3]*T4x + p[4]*T3x + p[5]*T2x + p[6]*x + \
        p[7]*T7y + p[8]*T6y + p[9]*T5y + p[10]*T4y + p[11]*T3y + p[12]*T2y + p[13]*y + \
        p[14]*T6x*y + p[15]*x*T6y + p[16]*T5x*T2y + p[17]*T2x*T5y + p[18]*T4x*T3y + p[19]*T3x*T4y + \
        p[20]*T5x*y + p[21]*x*T5y + p[22]*T4x*T2y + p[23]*T2x*T4y + p[24]*T3x*T3y + \
        p[25]*T4x*y + p[26]*x*T4y + p[27]*T3x*T2y + p[28]*T2x*T3y + \
        p[29]*T3x*y + p[30]*x*T3y + p[31]*T2x*T2y + \
        p[32]*T2x*y + p[33]*x*T2y + p[34]*x*y + p[35]
