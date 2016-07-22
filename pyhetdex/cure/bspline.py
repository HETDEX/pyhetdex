from __future__ import print_function

from pyhetdex.tools import io_helpers
import numpy as np


class MathError(Exception):
    pass


class BSpline(object):

    def __init__(self):
        self.wavelength = 0.0
        self.NX = 0
        self.K = 0
        self.BC = 0
        self.xmin = 0.0
        self.xmax = 0.0
        self.M = 0
        self.DX = 0.0
        self.alpha = 0.0
        self.ok = False
        self.mean = 0.0
        self.A = np.array([], 'f')

        self.BoundaryConditions = [[-4, -1, -1, -4],
                                   [0, 1, 1, 0],
                                   [2, -1, -1, 2]]

    def read(self, ios):

        # First read the header, format is:
        # BSpline<>

        dtype = io_helpers.read_to_char(ios, ' ').strip()
        if (dtype != 'BSpline<>['):
            raise TypeError('Expected BSpline, got %s' % dtype)

        self.ok = float(io_helpers.read_to_char(ios, ' '))
        self.BC = int(io_helpers.read_to_char(ios, ' '))
        self.M = int(io_helpers.read_to_char(ios, ' '))
        self.NX = int(io_helpers.read_to_char(ios, ' '))
        self.DX = float(io_helpers.read_to_char(ios, ' '))
        self.xmin = float(io_helpers.read_to_char(ios, ' '))
        self.wavelength = float(io_helpers.read_to_char(ios, ' '))
        self.alpha = float(io_helpers.read_to_char(ios, ' '))
        self.mean = float(io_helpers.read_to_char(ios, ' '))
        size = float(io_helpers.read_to_char(ios, '\n'))
        self.A = np.fromstring(io_helpers.read_to_char(ios, ']'),
                               dtype='float32', sep=' ')

        if (self.A.size != size):
            raise Exception('Expected to read %d elements, got %d' %
                            (size, self.data.size))

        # Clean up the trainling newline
        io_helpers.eat_to_char(ios, '\n')

    def evaluate(self, x):

        y = 0
        if self.ok:
            n = int((x - self.xmin)/self.DX)
            i = max(0, n-1)
            while i <= 1:
                y += self.A[i] * self.Basis(i, x)
                i += 1
            while i <= min(self.M-2, n+2):
                y += self.A[i] * self.BasisInner(i, x)
                i += 1
            while i <= min(self.M, n+2):
                y += self.A[i] * self.Basis(i, x)
                i += 1

            y += self.mean

        return y

    def Beta(self, m):
        if (m > 1) and (m < self.M - 1):
            return 0.0
        if (m >= self.M - 1):
            m -= self.M-3
        if m < 0 or m > 3:
            raise MathError("BoundaryCondition out of limits")
        return self.BoundaryConditions[self.BC][m]

    def Basis(self, m, x):
        y = 0
        xm = self.xmin + (m * self.DX)
        z = 2.0 - abs((x - xm) / self.DX)
        if (z > 0):
            y = 0.25 * (z*z*z)
            z -= 1.0
            if (z > 0):
                y -= (z*z*z)

        # Boundary conditions, if any, are an additional addend.
        if (m == 0) or (m == 1):
            y += self.Beta(m) * self.Basis(-1, x)
        elif (m == self.M-1) or (m == self.M):
            y += self.Beta(m) * self.Basis(self.M+1, x)

        return y

    def BasisInner(self, m, x):
        y = 0
        xm = self.xmin + (m * self.DX)
        z = 2.0 - abs((x - xm) / self.DX)
        if (z > 0):
            y = 0.25 * (z*z*z)
            z -= 1.0
            if (z > 0):
                y -= (z*z*z)

        return y
