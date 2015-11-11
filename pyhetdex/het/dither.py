"""Parse or create a dither file.

Create a dither file with :class:`DitherCreator` or :func:`create_dither_file`.

Fake an empty dither (:class:`EmptyDither`) or parse a dither file like the
following (:class:`ParseDither`) ::

    # basename          modelbase           ditherx dithery seeing norm airmass
    SIMDEX-obs-1_D1_046 SIMDEX-obs-1_D1_046   0.00   0.00    1.60  1.00  1.22
    SIMDEX-obs-1_D2_046 SIMDEX-obs-1_D2_046   0.61   1.07    1.60  1.00  1.22
    SIMDEX-obs-1_D3_046 SIMDEX-obs-1_D3_046   1.23   0.00    1.60  1.00  1.22

The :func:`create_dither_file` function is exposed via the ``dither_file``
executable
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import itertools as it
import re
import os

from numpy import array

from pyhetdex.het.fplane import FPlane
from pyhetdex.het.telescope import Shot
import pyhetdex.tools.files.file_tools as ft


class DitherParseError(ValueError):
    "Custom error"
    pass


class DitherCreationError(ValueError):
    "Raised when something fails while creating the dither file"
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
    """Class to create dither files

    Initialize the dither file creator for this shot

    Read in the locations of the dithers for each IFU from
    dither_positions.

    Parameters
    ----------
    dither_positions : str
        path to file containing the positions of the dithers for each
        IHMPID; the file must have the following format::

            ihmpid x1 x2 ... xn y1 y2 ... yn

    fplane_file : str
        path the focal plane file; it is parsed using
        :class:`~pyhetdex.het.fplane.FPlane`
    shot : :class:`pyhetdex.het.telescope.Shot` instance
        a ``shot`` instance that contains info on the image quality and
        normalization

    Attributes
    ----------
    ifu_dxs, ifu_dys : numpy arrays
        arrays of x and y shifts for the dithers
    shot
    fplane : :class:`~pyhetdex.het.fplane.FPlane` instance
    """
    def __init__(self, dither_positions, fplane_file, shot):
        self.ifu_dxs = {}
        self.ifu_dys = {}
        self.shot = shot
        self.fplane = FPlane(fplane_file)
        self._parse_dither_posistions(dither_positions)

    def _parse_dither_posistions(self, dither_positions):
        """Parse the file containing the dither positions"""
        # read in the file of dither positions
        with open(dither_positions, 'r') as f:
            for line in f:
                els = line.strip().split()
                if '#' in els[0]:
                    continue

                if len(els[1:]) % 2 == 1:
                    msg = ("The line '{}' in file '{} has a miss-matching"
                           " number of x and y entries")
                    raise DitherCreationError(msg.format(line,
                                                         dither_positions))
                else:
                    n_x = len(els[1:]) // 2
                # save dither positions in dictionary of IFUs
                #                      dither1 dither2  dither3
                self.ifu_dxs[els[0]] = array(els[1:n_x + 1], dtype=float)
                self.ifu_dys[els[0]] = array(els[n_x + 1:], dtype=float)

    def create_dither(self, id_, basenames, modelbases, outfile,
                      idtype='ifuid'):
        """ Create a dither file

        Parameters
        ----------
        id_ : str
            the id of the IFU
        basenames, modelnames : list of strings
            the root of the file and model (distortion, fiber etc);
            their lengths must be the same as :attr:`ifu_dxs`
        outfile : str
            the output filename
        idtype : str
            type of the id; must be one of ``'ifuid'``, ``'ihmpid'``,
            ``'specid'``
        """
        ifu = self.fplane.by_id(id_, idtype=idtype)
        dxs = self.ifu_dxs[ifu.ihmpid]
        dys = self.ifu_dys[ifu.ihmpid]

        if len(basenames) != len(dxs):
            msg = ("The number of elements in 'basenames' ({}) doesn't agree"
                   " with the expected number of dithers"
                   " ({})".format(len(basenames), len(dxs)))
            raise DitherCreationError(msg)
        if len(modelbases) != len(dxs):
            msg = ("The number of elements in 'modelbases' ({}) doesn't agree"
                   " with the expected number of dithers"
                   " ({})".format(len(modelbases), len(dxs)))
            raise DitherCreationError(msg)

        s = "# basename          modelbase           ditherx dithery\
                seeing norm airmass\n"
        line = "{:s} {:s} {:f} {:f} {:4.3f} {:5.4f} {:5.4f}\n"
        for dither, bn, mb, dx, dy in zip(it.count(), basenames, modelbases,
                                          dxs, dys):
            seeing = self.shot.fwhm(ifu.x, ifu.y, dither)
            norm = self.shot.normalisation(ifu.x, ifu.y, dither)
            # TODO replace with something
            airmass = 1.22

            s += line.format(bn, mb, dx, dy, seeing, norm, airmass)

        with open(outfile, 'w') as f:
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


def argument_parser(argv=None):
    """Parse the command line"""
    import argparse

    # Parse user input
    description = """Produce a dither file for the give id.
    """

    parser = argparse.ArgumentParser(description=description,
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('outfile', help="Name of a file to output")
    parser.add_argument('id', help="id of the chosen IFU")
    parser.add_argument('fplane', help="The fplane file")
    parser.add_argument('ditherpos', help='''Name of the file containing the
                         dither shifts. The expected format is
                         ``ihmpid x1 x2 ... xn y1 y2 ... yn``''')
    parser.add_argument('basename', help="""Basename of the data files. The
                        ``{dither}`` and ``{id}`` placeholders are replaced by
                        the dither number and the provided id. E.g., if the
                        ``id`` argument is ``001``, the string
                        ``file_D{dither}_{id}`` is replaced, for the first
                        dither, by file_D1_001. The placeholders don't have to
                        be present.""")

    parser.add_argument('-m', '--modelbase', help="""Basename of the model
                        files. It accepts that same place holders as
                        ``basename``""", default='masterflat_{id}')
    parser.add_argument('-t', '--id-type', help='Type of the id',
                        choices=['ifuid', 'ihmpid', 'specid'],
                        default='ihmpid')
    parser.add_argument('-s', '--shotdir', help="""Directory of the shot. If
                        not provided use some sensible default value for image
                        quality and normalisation""")

    return parser.parse_args(argv)


def create_dither_file(argv=None):
    """Function that creates the dither file

    Parameters
    ----------
    argv : list of strings
        if not provided sys.argv is used
    """
    args = argument_parser(argv=argv)

    # create the shot object
    shot = Shot(args.shotdir)

    # create the dither
    dithers = DitherCreator(args.ditherpos, args.fplane, shot)

    # generate modelbase and basenames for different dithers
    modelbases = []
    basenames = []
    for dither in range(len(dithers.ifu_dxs[args.id])):
        modelbases.append(args.modelbase.format(id=args.id, dither=dither + 1))
        basenames.append(args.basename.format(id=args.id, dither=dither + 1))

    dithers.create_dither(args.id, basenames, modelbases, args.outfile,
                          idtype=args.id_type)
