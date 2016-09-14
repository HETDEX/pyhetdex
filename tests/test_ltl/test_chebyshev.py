'''pyhetdex.ltl.chebyshev tests'''


import numpy as np
from numpy.polynomial.chebyshev import chebvander2d
import pytest

import pyhetdex.ltl.chebyshev as cheby

parametrize = pytest.mark.parametrize

# map between the indexes of the numpy.polynomial.chebyshev.chebvander2d and
# the ones from the pyhetdex implementation
index_map = [56, 48, 40, 32, 24, 16, 8,
             7, 6, 5, 4, 3, 2, 1,
             49, 14, 42, 21,
             35, 28, 41, 13,
             34, 20, 27, 33,
             12, 26, 19, 25,
             11, 18, 17, 10,
             9, 0]


x_y = parametrize('x, y',
                  [(3, 4), ([1, 2], 4), ([1, 2], [3, 4]),
                   pytest.mark.xfail(raises=ValueError,
                                     reason='Fail broadcasting')
                                    (([1, 2], [3, 4, 5]))])


@x_y
def test_matrixCheby2D_7(x, y):
    m = cheby.matrixCheby2D_7(x, y)
    nm = chebvander2d(np.array(x), np.array(y), [7, 7])

    for i, im in enumerate(index_map):
        assert (m[:, i] == nm[:, im]).all()


@x_y
def test_interpCheby2D_7(x, y):
    val = cheby.interpCheby2D_7(x, y, np.ones(36))

    nm = chebvander2d(np.array(x), np.array(y), [7, 7])[:, index_map]

    assert (val == nm.sum(axis=1)).all()
