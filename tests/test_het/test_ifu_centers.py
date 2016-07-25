'''test the parsing of the IFUcen files'''

import textwrap as tw
import pytest

import pyhetdex.het.ifu_centers as ifucen

parametrize = pytest.mark.parametrize

xfail_ifucen = pytest.mark.xfail(raises=ifucen.IFUCenterError,
                                 reason="Failures in parsing the IFUcen file")


@parametrize('lines, channels, n_fibers',
             [(['0001 -19.8000 -19.6876 L 0001 1.000', ], ['L', ], [1, ]),
              (['0001 -19.8000 -19.6876 R 0001 1.000', ], ['R', ], [1, ]),
              (['0001 -19.8000 -19.6876 L 0001 1.000',
                '0001 -19.8000 -19.6876 L 0002 1.000',
                '0001 -19.8000 -19.6876 R 0001 1.000', ], ['R', 'L'], [1, 2]),
              (['0001 -19.8000 -19.6876 L 0001 1.000',
                '# 0001 -19.8000 -19.6876 L 0002 1.000',
                '0001 -19.8000 -19.6876 R 0001 1.000', ], ['R', 'L'], [1, 1]),
              (['0001 -19.8000 -19.6876 L -- 1.000',
                '0001 -19.8000 -19.6876 L 0002 1.000',
                '0001 -19.8000 -19.6876 R 0001 1.000', ], ['R', 'L'], [1, 1]),
              (['0001 -19.8000 -19.6876 L -001 1.000',
                '0001 -19.8000 -19.6876 L 0002 1.000',
                '0001 -19.8000 -19.6876 R 0001 1.000', ], ['R', 'L'], [1, 1]),
              xfail_ifucen((['0001 -19.8000 -19.6876 L 0001 -1.000'], [], [])),
              ])
def test_ifu_centers(tmpdir, lines, channels, n_fibers):
    '''Create a temporary IFU cen files and try to parse it'''
    ifucenter = tmpdir.join('IFUcenter.txt')
    header = tw.dedent("""\
                       # Extra comment
                       # IFU 00001
                       # FIBERD   FIBERSEP
                       1.55      2.20
                       # NFIBX NFIBY
                       20 23
                       #
                       """)
    ifucenter.write(header)
    for l in lines:
        ifucenter.write(l + '\n', mode='a')

    ifu_cen = ifucen.IFUCenter(ifucenter.strpath)

    assert sorted(ifu_cen.channels) == sorted(channels)
    for c, n in zip(channels, n_fibers):
        assert ifu_cen.n_fibers[c] == n
        assert len(ifu_cen.fib_number[c]) == n


@pytest.mark.xfail(raises=ifucen.IFUCenterError,
                   reason="Fail to parse the IFUcen file because of header")
def test_ifu_centers_missingid(tmpdir):
    "Test missing ID string in header"
    ifucenter = tmpdir.join('IFUcenter.txt')
    header = tw.dedent("""\
                       1.55      2.20
                       20 23
                       #
                       """)
    ifucenter.write(header)

    ifucen.IFUCenter(ifucenter.strpath)
