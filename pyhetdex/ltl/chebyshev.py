from __future__ import absolute_import, print_function

import numpy as np
from numpy.polynomial.chebyshev import chebvander


def matrixCheby2D_7(x, y):
    '''Create and return a 2D array of Tx_i, Ty_j ordered as needed for use
    with cure distortion solutions.

    Parameters
    ----------
    x, y : numbers or ndarray-like
        values of x and y where to compute the Ts

    Returns
    -------
    two dimensional array with len(x) rows and 36 columns
    '''

    T0x, T1x, T2x, T3x, T4x, T5x, T6x, T7x = chebvander(x, 7).T
    T0y, T1y, T2y, T3y, T4y, T5y, T6y, T7y = chebvander(y, 7).T

    return np.vstack(np.broadcast_arrays(T7x, T6x, T5x, T4x, T3x, T2x, T1x,
                                         T7y, T6y, T5y, T4y, T3y, T2y, T1y,
                                         T6x*T1y, T1x*T6y, T5x*T2y, T2x*T5y,
                                         T4x*T3y, T3x*T4y, T5x*T1y, T1x*T5y,
                                         T4x*T2y, T2x*T4y, T3x*T3y, T4x*T1y,
                                         T1x*T4y, T3x*T2y, T2x*T3y, T3x*T1y,
                                         T1x*T3y, T2x*T2y, T2x*T1y, T1x*T2y,
                                         T1x*T1y, T0x)).T


def interpCheby2D_7(x, y, p):
    '''Evaluate the 2D, 7th order, Chebyshev series at values x, y.

    Parameters
    ----------
    x, y : numbers or ndarray-like
        values of x and y where to evaluate the series
    p : ndarray-like
        coefficient ordered according to cure distortion output.

    Returns
    -------
    ndarray
        array of evaluations
    '''

    M = matrixCheby2D_7(x, y)

    return np.dot(M, p)
