"""
Anything related with the HETDEX dither files should go here
"""

from __future__ import print_function, absolute_import

import re

import pyhetdex.common.file_tools as ft


# read and parse the dither file
class _BaseDither(object):
    """
    Base class for the dither object. Just defines the common public variables
    """

    def __init__(self):
        # common prefix of the L and R file names of the dither
        self.basename = {}
        # delta x and y of the dithers
        self.dx, self.dy = {}, {}
        # image quality, illumination and airmass
        self.seeing, self.norm, self.airmass = {}, {}, {}


class EmptyDither(_BaseDither):
    """
    Creates a dither object with only one entry. The dither key is "D1",
    basename is left emtpy, dx and dy are set to 0 and image quality,
    illumination and airmass are set to one.
    It is provided as a stub dither object in case the real one does not
    exists.
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
    Parse the dither file and store the informations in dictionaries with the
    string 'Di', with i=1,2,3, as key
    """

    def __init__(self, dither_file):
        """
        Parse the dither file and store the relevant information
        Parameters
        ----------
        dither_file: string
            file containing the dither relative position. If None a single
            dither added
        """
        super(ParseDither, self).__init__()
        self._read_dither(dither_file)

    def _read_dither(self, dither_file):
        """
        Read the relative dither position
        Parameters
        ----------
        dither_file: string
            file containing the dither relative position. If None a single
            dither added
        """
        with open(dither_file, 'r') as f:
            f = ft.skip_comments(f)
            for l in f:
                try:
                    _bn, _d, _x, _y, _seeing, _norm, _airmass = l.split()
                    _d = list(set(re.findall(r'D\d', _d)))
                    if len(_d) != 1:
                        msg = "While extracting the dither number from the"
                        msg += " basename in the dither file, {} matches to"
                        msg += " 'D\\d' expression where found. I expected"
                        msg += " one. What should I do?"
                        raise ValueError(msg.format(len(_d)))
                    self.basename[_d] = _bn
                    self.dx[_d] = float(_x)
                    self.dy[_d] = float(_y)
                    self.seeing[_d] = float(_seeing)
                    self.norm[_d] = float(_norm)
                    self.airmass[_d] = float(_airmass)
                except ValueError:
                    # skip empty lines
                    pass
