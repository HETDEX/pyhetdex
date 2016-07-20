"""Test pyhetdetyx.het.dither"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import filecmp

import pytest

from pyhetdex.het.telescope import Shot
from pyhetdex.het import dither

parametrize = pytest.mark.parametrize


@pytest.fixture
def tmp_dither_file(tmpdir):
    """Returns the name of a dither file in a tmp directory as a py.path
    object"""
    return tmpdir.join('tmp.dither.txt')


@pytest.fixture
def shot():
    """Create and returns a pyhetdex.het.telescope.Shot object"""
    return Shot()


@pytest.fixture
def dither_creator(ditherpos_file, fplane_file, shot):
    """Create and return a DitherCreator object"""
    return dither.DitherCreator.from_file(str(fplane_file), shot,
                                          str(ditherpos_file))


@pytest.fixture
def ditherpos_046():
    '''Return the list of dither positions for IFU slot 046'''
    return ['0.000', '0.615', '1.230', '0.000', '1.065', '0.000']


@pytest.fixture
def ditherpos_file_list(ditherpos_file):
    '''Returns the dither position file as list wrapped into a list'''
    return [ditherpos_file.strpath]

xfail_dither_create = pytest.mark.xfail(raises=dither.DitherCreationError,
                                        reason="Wrong number of basenames")

xfail_system_exit = pytest.mark.xfail(raises=SystemExit,
                                      reason="The entry point exited")


def test_empty_dithers():
    "Empty dither"
    dithers = dither.EmptyDither()
    assert len(dithers.dithers) == 1


def test_parse_dither_file(dither_fast):
    "Parse the dither file"
    dither_fast = str(dither_fast)
    dithers = dither.ParseDither(dither_fast)
    assert len(dithers.dithers) == 3
    assert dithers.filename == os.path.split(dither_fast)[1]
    assert dithers.abspath == os.path.split(dither_fast)[0]


def test_parse_dither_file_empty_line(tmpdir):
    "Parse the dither file"
    dither_file = tmpdir.join('dither.txt')
    dither_file.write('base_D1 model_D1 1 2 1 1 1\n'
                      '\nbase_D3 model_D2 1 2 1 1 1')
    dither_file = str(dither_file)
    dithers = dither.ParseDither(dither_file)
    assert len(dithers.dithers) == 2
    assert dithers.filename == os.path.split(dither_file)[1]
    assert dithers.abspath == os.path.split(dither_file)[0]


@pytest.mark.xfail(raises=dither.DitherParseError,
                   reason="Wrong format for the dither file")
def test_wrong_dither(dither_wrong):
    "Fail in parsing a dither without 'D[123]' in basename"
    dither.ParseDither(str(dither_wrong))


@parametrize('basenames, modelbases',
             [(['fast_SIMDEX-4000-obs-1_D1_046',
                'fast_SIMDEX-4000-obs-1_D2_046',
                'fast_SIMDEX-4000-obs-1_D3_046'],
               ['fast_SIMDEX-4000-obs-1_D1_046',
                'fast_SIMDEX-4000-obs-1_D2_046',
                'fast_SIMDEX-4000-obs-1_D3_046']),
              xfail_dither_create((['1', '2'], [])),
              xfail_dither_create((['1', '2', '3'], ['1'])),
              ])
def test_dither_creator(dither_creator, tmp_dither_file, example_fdither,
                        basenames, modelbases):
    """Test if the dither file is created successfully"""
    dither_creator.create_dither('023', basenames, modelbases,
                                 str(tmp_dither_file))

    same_file = filecmp.cmp(str(tmp_dither_file), str(example_fdither))
    assert same_file


@pytest.mark.xfail(raises=dither.DitherPositionError,
                   reason="Fail to parse the dither position file")
def test_dither_creator_wrong_number_dithers(fplane_file, shot):
    """Test the case in which the number of dither positions is odd"""

    dither.DitherCreator(str(fplane_file), shot,
                         dither_positions=[['001', 2, 3, 4]])


@parametrize('option, fixture',
             [('-f', 'ditherpos_file_list'), ('-d', 'ditherpos_046')])
@parametrize('basenames, modelbases',
             [(['fast_SIMDEX-4000-obs-1_D{dither}_{id}', ],
               ['fast_SIMDEX-4000-obs-1_D{dither}_{id}', ]),
              (['fast_SIMDEX-4000-obs-1_D1_046',
                'fast_SIMDEX-4000-obs-1_D2_046',
                'fast_SIMDEX-4000-obs-1_D3_046'],
               ['fast_SIMDEX-4000-obs-1_D1_046',
                'fast_SIMDEX-4000-obs-1_D2_046',
                'fast_SIMDEX-4000-obs-1_D3_046']),
              (['fast_SIMDEX-4000-obs-1_D{dither}_{id}', ],
               ['fast_SIMDEX-4000-obs-1_D1_046',
                'fast_SIMDEX-4000-obs-1_D2_046',
                'fast_SIMDEX-4000-obs-1_D3_046']),
              (['fast_SIMDEX-4000-obs-1_D1_046',
                'fast_SIMDEX-4000-obs-1_D2_046',
                'fast_SIMDEX-4000-obs-1_D3_046'],
               ['fast_SIMDEX-4000-obs-1_D{dither}_{id}', ]),
              xfail_system_exit((['1', '2'], [])),
              xfail_system_exit((['1', ], ['1', '2'])),
              ])
def test_command_line_dithertool(request, tmp_dither_file, fplane_file,
                                 example_fdither, basenames, modelbases,
                                 option, fixture):
    """Test the command line tool to create the dither file works"""

    args = ['--modelbase', ] + modelbases + ['-o', str(tmp_dither_file)]
    args += [option, ] + request.getfuncargvalue(fixture)
    args += ['--', '046', str(fplane_file), ] + basenames

    dither.create_dither_file(argv=args)

    same_file = filecmp.cmp(str(tmp_dither_file), str(example_fdither))
    assert same_file


@pytest.mark.xfail(raises=SystemExit,
                   reason=('It is not possible to give both the dither'
                           ' positions and the dither position file'))
def test_command_line_dithertool_exclusive():
    dither.create_dither_file(argv=['-d', '1', '2', '-f', 'dpos.txt',
                                    '046', 'fplane.txt', 'basename'])


def test_command_line_dithertool_header(datadir, tmp_dither_file, fplane_file,
                                        ditherpos_file, example_fdither):
    """Make sure that the output file when orderding by some header keyword is
    fine"""
    args = ['--modelbase', 'fast_SIMDEX-4000-obs-1_D{dither}_{id}']
    args += ['-o', str(tmp_dither_file), '-O', 'DITHER']
    args += ['-f', str(ditherpos_file)]
    args += ['046', str(fplane_file)]
    args += [str(datadir.join(f)) for f in ['fast_SIMDEX-4000-obs-1_D2_046',
                                            'fast_SIMDEX-4000-obs-1_D3_046',
                                            'fast_SIMDEX-4000-obs-1_D1_046']]

    dither.create_dither_file(argv=args)

    example_file = example_fdither.readlines(cr=False)
    dither_file = tmp_dither_file.readlines(cr=False)
    for ef, df in zip(example_file, dither_file):
        assert ef in df


def test_command_line_dithertool_hetpupil(datadir, example_fdither,
                                          skip_if_no_executable,
                                          tmp_dither_file, fplane_file,
                                          ditherpos_046):
    '''Test using the hetpupil model'''
    skip_if_no_executable('hetpupil')

    args = ['--modelbase', 'fast_SIMDEX-4000-obs-1_D{dither}_{id}']
    args += ['-d'] + ditherpos_046
    args += ['-o', str(tmp_dither_file), '--use-hetpupil']
    args += ['046', str(fplane_file),
             datadir.join('fast_SIMDEX-4000-obs-1_D{dither}_{id}').strpath]

    dither.create_dither_file(argv=args)

    example_file = example_fdither.readlines(cr=False)
    dither_file = tmp_dither_file.readlines(cr=False)
    for ef, df in zip(example_file, dither_file):
        assert ef in df
