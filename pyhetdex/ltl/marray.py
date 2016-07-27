from __future__ import absolute_import, print_function

__version__ = '$Id$'

import numpy as np
from pyhetdex.tools import io_helpers


class FVector(object):
    ''' Python class allowing reading / writing of ltl/FVector object.'''

    def __init__(self, fname=None):
        self._data = None

        if fname:
            infile = open(fname, 'r')
            self.read(infile)
            infile.close()

    @property
    def data(self):
        """The internal numpy array holding the data"""

        return self._data

    @data.setter
    def data(self, dat):

        if type(dat) != np.ndarray:
            raise TypeError('Data type for FVector must be a numpy array')
        if dat.ndim != 1:
            raise TypeError('Array must be one dimensional for FVector')
        if 'float' not in dat.dtype.name:
            if 'int' not in dat.dtype.name:
                raise TypeError('Only int, float and double are supported!')
        self._data = dat

    def read(self, ios):

        # First read the header, format is:
        # FVector< T,36,0 >

        dtype = io_helpers.read_to_char(ios, '<').strip()
        if (dtype != 'FVector'):
            raise TypeError('Expected FVector, got %s' % dtype)

        ftype = io_helpers.read_to_char(ios, ',')  # Forward through  < T,
        ftype = ftype.strip()
        if ftype not in ('float', 'double', 'int', 'T'):
            raise TypeError('Unsupported datatype!')
        elif ftype == 'T':
            print('Warning the datatype is unknown, assuming float!')
            ftype = 'float'
        elif ftype == 'float':
            ftype = 'float32'

        # Read size to next ,
        size = int(io_helpers.read_to_char(ios, ','))

        stride = int(io_helpers.read_to_char(ios, '>'))
        if (stride != 0):
            raise Exception('Only stride 0 is supported')

        # Read actual data in
        # Data is in format  [ 6.4277265720642998e+00 4.6045159399542094e+01]
        # Could span several lines
        io_helpers.eat_to_blockstart(ios)  # Go to start of data

        self.data = np.fromstring(io_helpers.read_to_char(ios, ']'),
                                  dtype=ftype, sep=' ')

        if (self.data.size != size):
            raise Exception('Expected to read %d elements, got %d' %
                            (size, self.data.size))

        # Clean up the trainling newline
        io_helpers.eat_to_char(ios, '\n')

    def write(self, ios):

        if self.data is None:
            raise Exception('Cowardly refusing to write empty FVector')
        ios.write("FVector< ")

        if 'float64' in self._data.dtype.name:
            ios.write('double,')
            frmt = ' %.6e'
        elif 'float' in self._data.dtype.name:
            ios.write('float,')
            frmt = ' %.6e'
        elif 'int' in self._data.dtype.name:
            ios.write('int,')
            frmt = ' %d'
        else:
            raise TypeError('Unexpected data type!')

        ios.write("%d,0 >\n " % self.data.size)
        ios.write("[")
        for i in range(0, self.data.size):
            ios.write(frmt % self.data[i])
            if not ((i+1) % 9):
                ios.write(' \n ')

        ios.write("  ]\n")  # LTL writes two spaces before final ]


class MArray(object):
    ''' Python class allowing reading / writing of ltl/MArray object.'''

    def __init__(self, fname=None):
        self._data = None
        self.shapes = []

        if fname:
            infile = open(fname, 'r')
            self.read(infile)
            infile.close()

    @property
    def data(self):
        """The internal numpy array holding the data"""

        return self._data

    @data.setter
    def data(self, dat):
        if type(dat) != np.ndarray:
            raise TypeError('Data type for MArray must be a numpy array')

        if 'float' not in dat.dtype.name:
            if 'int' not in dat.dtype.name:
                raise TypeError('Only int, float and double are supported!')

        self._data = dat
        self.shapes = []
        for d in range(dat.ndim):
            self.shapes.append('1,%d' % dat.shape[d])

    def read(self, ios):

        # First read the header, format is:
        # MArray<T,2> ( 14 x 246 ) : (1,14) (1,246)

        dtype = io_helpers.read_to_char(ios, '<').strip()
        if (dtype != 'MArray'):
            raise TypeError('Expected MArray, got %s' % dtype)

        ftype = io_helpers.read_to_char(ios, ',')  # Forward through  < T,
        ftype = ftype.strip()
        if ftype not in ('float', 'double', 'int', 'T'):
            raise TypeError('Unsupported datatype!')
        elif ftype == 'T':
            print('Warning the datatype is unknown, assuming float!')
            ftype = 'float'
        elif ftype == 'float':
            ftype = 'float32'

        ndims = int(io_helpers.read_to_char(ios, '>'))  # Read dimensionsdd)

        io_helpers.eat_to_char(ios, '(')  # Forward to sizes

        shapes = []
        size = []

        d = 1
        while (d < ndims):
            size.append(int(io_helpers.read_to_char(ios, 'x')))
            d += 1

        size.append(int(io_helpers.read_to_char(ios, ')')))

        d = 0
        while (d < ndims):
            io_helpers.eat_to_char(ios, '(')
            shapes.append(io_helpers.read_to_char(ios, ')'))
            d += 1

        # ios.readline() # Read rest of descriptor line

        # Read actual data in
        # Data is in format  [ 6.4277265720642998e+00 4.6045159399542094e+01]
        # Could span several lines

        # Allocate data array
        size.reverse()
        data = np.zeros(size, ftype)
        size.reverse()

        # Read actual data in
        io_helpers.eat_to_blockstart(ios)

        # Now we are at the beginning of the first data block

        i = 0
        while (i < data.size):
            val = io_helpers.read_to_char(ios, ']')
            data.flat[i:i+size[0]] = np.fromstring(val, dtype=ftype,
                                                   sep=' ')
            i = i + size[0]
            if(i < data.size):
                io_helpers.eat_to_blockstart(ios)

        self.data = data.transpose()
        self.shapes = shapes

        # Clean up the trailing newline
        io_helpers.eat_to_char(ios, '\n')

    def write(self, ios):

        # Write header line
        ios.write("MArray<")
        if 'float64' in self._data.dtype.name:
            ios.write('double,')
            frmt = ' %.6e'
        elif 'float' in self._data.dtype.name:
            ios.write('float,')
            frmt = ' %.6e'
        elif 'int' in self._data.dtype.name:
            ios.write('int,')
            frmt = ' %d'
        else:
            raise TypeError('Unexpected data type!')

        ios.write('%d> ( %d' % (self._data.ndim, self._data.shape[0]))

        d = 1
        while d < self._data.ndim:
            ios.write(' x %d' % self._data.shape[d])
            d += 1

        ios.write(' ) :')

        for d in range(self._data.ndim):
            ios.write(' (%s)' % self.shapes[d])
        ios.write(' \n')

        # Write the data

        self.__recursive_write(ios, self._data, 0, ' ', frmt)
        ios.write(']\n')

    def __recursive_write(self, ios, data, i, pad, frmt):
        ios.write('[')
        if (data.ndim > 1):
            while (i < data.shape[-1]):
                self.__recursive_write(ios, data[..., i], 0, pad+' ', frmt)
                i = i+1
                ios.write(']')
                if(i < data.shape[-1]):
                    ios.write('\n'+pad)
        else:
            for j in range(0, data.size):
                ios.write(frmt % data[j])
                # if not ((j+1) % 9):
                #    ios.write('\n'+pad)
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
