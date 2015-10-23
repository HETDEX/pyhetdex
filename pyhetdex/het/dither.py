"""Fake an empty dither (:class:`EmptyDither`) or parse a dither file like the
following (:class:`ParseDither`) ::

    # basename          modelbase           ditherx dithery seeing norm airmass
    SIMDEX-obs-1_D1_046 SIMDEX-obs-1_D1_046   0.00   0.00    1.60  1.00  1.22
    SIMDEX-obs-1_D2_046 SIMDEX-obs-1_D2_046   0.61   1.07    1.60  1.00  1.22
    SIMDEX-obs-1_D3_046 SIMDEX-obs-1_D3_046   1.23   0.00    1.60  1.00  1.22

"""

from __future__ import print_function, absolute_import

import os
import re

from numpy import array
from pyhetdex.het.fplane import FPlane
from pyhetdex.het.telescope import Shot
import pyhetdex.tools.files.file_tools as ft


class DitherParseError(ValueError):
    "Custom error"
    pass


# read and parse the dither file
class _BaseDither(object):
    """Base class for the dither object. Just defines the common public
    variables

    Attributes
    ----------
    basename : dictionary
        basenames of the dither files; key : dither; value: basename
    dx, dy : dictionaries
        dither relative x and y position; key : dither; value: dx, dy
    seeing : dictionary
        dither image quality; key dither; value : image quality
    norm : dictionary
        relative flux normalisation among dithers; key dither; value :
        normalisation
    airmass : dictionary
        dither airmass; key dither; value : airmass
    """
    def __init__(self):
        # common prefix of the L and R file names of the dither
        self.basename = {}
        # delta x and y of the dithers
        self.dx, self.dy = {}, {}
        # image quality, illumination and airmass
        self.seeing, self.norm, self.airmass = {}, {}, {}
        # remember the dither file name
        self._absfname = ''

    @property
    def dithers(self):
        """ List of dithers """
        return list(self.basename.keys())

    @property
    def absfname(self):
        """Absolute file name"""
        return self._absfname

    @property
    def abspath(self):
        """ Absolute file path """
        return os.path.split(self.absfname)[0]

    @property
    def filename(self):
        """ Absolute file path """
        return os.path.split(self.absfname)[1]


class DitherCreator(object):
    """ Class to create dither files """

    def __init__(self, dither_positions, fplane_file, shot):
        """ Initialize the dither file creator for this shot
        
        Read in the locations of the dithers for each IFU from
        dither_positions.

        Parameters
        ----------
        dither_positions : str
            path to file containing the positions of 
            the dithers for each IHMPID
        fplane_file : str
            path the focal plane file
        shot : `class:` pyhetdex.het.telescope.Shot 
            a `shot` instance that contains info on the  
        """

        self.ifu_dxs = {}
        self.ifu_dys = {}
        self.shot = shot
        self.fplane = FPlane(fplane_file)       

 
        # read in the file of dither positions
        with open(dither_positions, 'r') as f:
            for line in f:
                els = line.strip().split()
                if '#' in els[0]:
                    continue
 
                # save dither positions in dictionary of IFUs
                #                            dither1 dither2  dither3
                self.ifu_dxs[els[0]] = array([els[1], els[2], els[3]], dtype=float)
                self.ifu_dys[els[0]] = array([els[4], els[5], els[6]], dtype=float)

    def create_dither(self, ifuid, basenames, modelbases, outfile):
        """ Create a dither file

        Parameters
        ----------
        ifuid : str
            the id of the IFU
        basenames, modelnames : list of strings
            the root of the file and model (distortion, fiber etc)
            filenames of the three dithers
        outfile : str
            the output filename
        """

        ifu = self.fplane.difus[ifuid] 

        with open(outfile, 'w') as f:
            s = "# basename          modelbase           ditherx dithery seeing norm airmass\n"
            for dither in range(3):

                seeing = self.shot.fwhm(ifu.x, ifu.y, dither)
                norm = self.shot.normalisation(ifu.x, ifu.y, dither)
                airmass = 1.22 # XXX replace with something
                ditherx = (self.ifu_dxs[ifu.ihmpid])[dither]
                dithery = (self.ifu_dys[ifu.ihmpid])[dither]

                s += "{:s} {:s} {:f} {:f} {:4.3f} {:5.4f} {:5.4f}\n".format(basenames[dither],
                                                                            modelbases[dither],
                                                                            ditherx, dithery,
                                                                            seeing, norm,  
                                                                            airmass)
            f.write(s)
                                                                      
                                                                        
                                                                    
class EmptyDither(_BaseDither):
    """Creates a dither object with only one entry.

    The dither key is **D1**, ``basename`` and ``absfname`` are left empty,
    ``dx`` and ``dy`` are set to 0 and image quality, illumination and airmass
    are set to 1. It is provided as a stub dither object in case the real one
    does not exists.
    """
    def __init__(self):
        super(EmptyDither, self).__init__()
        self._no_dither()

    def _no_dither(self):
        "Fake a single dither"
        _d = "D1"
        self.basename[_d] = ""
        self.dx[_d] = 0.
        self.dy[_d] = 0.
        self.seeing[_d] = 1.
        self.norm[_d] = 1.
        self.airmass[_d] = 1.


class ParseDither(_BaseDither):
    """
    Parse the dither file and store the information in dictionaries with the
    string ``Di``, with i=1,2,3, as key

    Parameters
    ----------
    dither_file : string
        file containing the dither relative position.

    Raises
    ------
    DitherParseError
        if the key ``Di`` is not found in the base name
    """

    def __init__(self, dither_file):
        super(ParseDither, self).__init__()
        self._absfname = os.path.abspath(dither_file)
        self._read_dither(dither_file)

    def _read_dither(self, dither_file):
        """
        Read the relative dither position

        Parameters
        ----------
        dither_file : string
            file containing the dither relative position. If None a single
            dither added
        """
        with open(dither_file, 'r') as f:
            f = ft.skip_comments(f)
            for l in f:
                try:
                    _bn, _d, _x, _y, _seeing, _norm, _airmass = l.split()
                except ValueError:  # skip empty or incomplete lines
                    pass
                try:
                    _d = list(set(re.findall(r'D\d', _d)))[0]
                except IndexError:
                    msg = "While extracting the dither number from the"
                    msg += " basename in the dither file, {} matches to"
                    msg += " 'D\\d' expression where found. I expected"
                    msg += " one. What should I do?"
                    raise DitherParseError(msg.format(len(_d)))
                self.basename[_d] = _bn
                self.dx[_d] = float(_x)
                self.dy[_d] = float(_y)
                self.seeing[_d] = float(_seeing)
                self.norm[_d] = float(_norm)
                self.airmass[_d] = float(_airmass)


def create_dither_file(argv=None):

    import argparse
    import sys

    # Parse user input
    parser = argparse.ArgumentParser(description='Produce a dither file')
    parser.add_argument('outfile', type=str, help="Name of a file to output")
    parser.add_argument('ifuid', type=str, help="id of the chosen IFU") 
    parser.add_argument('fplane', type=str, help="The fplane file")
    parser.add_argument('ditherpos', type=str, help='List of dither positions per ifu')
    parser.add_argument('basename', type=str, help="Basename of the data files")
    parser.add_argument('modelbase', type=str, help="Basename of the model files")
    parser.add_argument('--shotdir', type=str, help="Directory of the shot",
                        default='.') 
    input = parser.parse_args(argv)
   
    # generate modelbase and basenames for different dithers
    modelbases = []
    basenames = []
    for suff in ['D1', 'D2', 'D3']:
        # ..todo should it be IHMPID here? (not ifu id)
        modelbases.append(input.modelbase + suff + "_{:s}".format(input.ifuid))
        basenames.append(input.basename + suff + "_{:s}".format(input.ifuid))


    # create the shot object
    shot = Shot(input.shotdir)

    # create the dither
    dithers = DitherCreator(input.ditherpos, input.fplane, shot)
    dithers.create_dither(input.ifuid, basenames, modelbases, input.outfile)










 















