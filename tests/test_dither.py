"""Test pyhetdetyx.het.dither"""

from os.path import join
from os import remove
import filecmp
import nose

from pyhetdex.het.telescope import Shot
from pyhetdex.het.dither import DitherCreator, create_dither_file
from settings import datadir 



class TestDitherCreator(object):
    """ Test the DitherCreator class"""
    outfile = join(datadir, 'tmp.dither.txt')
    example_fdither = join(datadir, 'dither.example.txt')

    @classmethod
    def setup_class(cls):
        # create a shot object
        shot = Shot(datadir)
        cls.ditherpos = join(datadir, "dither_positions.txt")
        cls.fplane = join(datadir, 'fplane.txt') 

        # create the dither creator
        cls.dithers = DitherCreator(cls.ditherpos, cls.fplane, shot)

        return cls


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
        remove(cls.outfile)

    def test_command_line_dithertool(cls):
        """Test the command line tool to create the dither file works"""

        args = [cls.outfile, 
                '046', 
                cls.fplane, 
                cls.ditherpos, 
                'fast_SIMDEX-4000-obs-1_', 
                'fast_SIMDEX-4000-obs-1_']

        create_dither_file(argv=args)        

        same_file = filecmp.cmp(cls.outfile, cls.example_fdither)
        assert same_file
        remove(cls.outfile)



  



