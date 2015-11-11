"""Test pyhetdetyx.het.dither"""

import os
from os.path import join
from os import remove
import filecmp

import pytest

from pyhetdex.het.telescope import Shot
from pyhetdex.het import dither

from settings import datadir

dither_fast = os.path.join(datadir, "dither_fast_SIMDEX-4000-obs-1_046.txt")
dither_wrong = os.path.join(datadir,
                            "dither_wrong_SIMDEX-4000-obs-1_046.txt")


class TestDither(object):
    "Parse the dither files"
    def test_empty_dithers(self):
        "Empty dither"
        dithers = dither.EmptyDither()
        assert len(dithers.dithers) == 1

    def test_dithers(self):
        "Parse the dither file"
        dithers = dither.ParseDither(dither_fast)
        assert len(dithers.dithers) == 3
        assert dithers.filename == os.path.split(dither_fast)[1]
        assert dithers.abspath == os.path.split(dither_fast)[0]

    @pytest.mark.xfail(raises=dither.DitherParseError,
                       reason="Wrong format for the dither file")
    def test_wrong_dither(self):
        "Fail in parsing a dither without 'D[123]' in basename"
        dither.ParseDither(dither_wrong)


class TestDitherCreator(object):
    """ Test the DitherCreator class"""
    outfile = os.path.join(datadir, 'tmp.dither.txt')
    example_fdither = os.path.join(datadir, 'dither.example.txt')

    @classmethod
    def setup_class(cls):
        # create a shot object
        shot = Shot(datadir)
        cls.ditherpos = join(datadir, "dither_positions.txt")
        cls.fplane = join(datadir, 'fplane.txt')

        # create the dither creator
        cls.dithers = dither.DitherCreator(cls.ditherpos, cls.fplane, shot)

        return cls

    @classmethod
    def teardown_class(cls):
        remove(cls.outfile)

    def test_dither_creation(cls):
        """Test if the dither file is created successfully"""

        cls.dithers.create_dither('046',
                                  ['fast_SIMDEX-4000-obs-1_D1_046',
                                   'fast_SIMDEX-4000-obs-1_D2_046',
                                   'fast_SIMDEX-4000-obs-1_D3_046'],
                                  ['fast_SIMDEX-4000-obs-1_D1_046',
                                   'fast_SIMDEX-4000-obs-1_D2_046',
                                   'fast_SIMDEX-4000-obs-1_D3_046'],
                                  cls.outfile)

        same_file = filecmp.cmp(cls.outfile, cls.example_fdither)
        assert same_file

    @pytest.mark.xfail(raises=dither.DitherCreationError,
                       reason="Wrong number of basenames")
    def test_wrong_basenames(cls):
        cls.dithers.create_dither('046',
                                  ['fast_SIMDEX-4000-obs-1_D1_046',
                                   'fast_SIMDEX-4000-obs-1_D3_046'],
                                  [], cls.outfile)

    @pytest.mark.xfail(raises=dither.DitherCreationError,
                       reason="Wrong number of modelbase")
    def test_wrong_modelbase(cls):
        cls.dithers.create_dither('046',
                                  ['fast_SIMDEX-4000-obs-1_D1_046',
                                   'fast_SIMDEX-4000-obs-1_D2_046',
                                   'fast_SIMDEX-4000-obs-1_D3_046'],
                                  ['fast_SIMDEX-4000-obs-1_D1_046',
                                   'fast_SIMDEX-4000-obs-1_D3_046'],
                                  cls.outfile)

    def test_command_line_dithertool(cls):
        """Test the command line tool to create the dither file works"""

        args = ['--modelbase',
                'fast_SIMDEX-4000-obs-1_D{dither}_{id}',
                cls.outfile,
                '046',
                cls.fplane,
                cls.ditherpos,
                'fast_SIMDEX-4000-obs-1_D{dither}_{id}',
                ]

        dither.create_dither_file(argv=args)

        same_file = filecmp.cmp(cls.outfile, cls.example_fdither)
        assert same_file
