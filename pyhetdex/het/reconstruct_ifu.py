"""
Parse the ifu center file and reconstruct the IFU
"""

from __future__ import print_function, absolute_import

from collections import defaultdict
import itertools as it

from astropy.io import fits
import numpy as np

from pyhetdex.common.fitstools import wavelength_to_index
import pyhetdex.common.file_tools as ft
from pyhetdex.het import dither


# TODO: Separate the following class into one to parse the IFU center file and
# one to do the actual reconstruction give the dither and the IFu center
# objects
class ReconstructedIFU(object):
    """
    Reconstructed IFU head given the *ifu_center_file* and if any, the dither
    file.
    """

    def __init__(self, ifu_center_file, dither_file=None, fextract=None):
        """
        Read and parse the file
        Parameters
        ----------
        ifu_center_file: string
            file containing the fiber number to fiber position mapping
        dither_file: string
            file containing the dither relative position. If not given, a singe
            dither is assumed
        fextract: None or list of fits files
            if None the list of files is inferred from first or second column
            of the *dither_file*;
            if not None must have *ndither* x *nchannels* elements. The channel
            name and dither number are extracted from the *CCDPOS* and the
            *DITHER* header keywords
        WARNING: *dither_file* and *fextract* cannot be *None* at the same time
        WARNING: if *dither_file* is None, *fextract* must contain a number of
        files equal  to the number of channels (2)
        NOTE: should this distinction be moved to factory functions?
        """
        if dither_file is None and fextract is None:
            msg = "dither_file and/or fextract must be provided"
            raise ValueError(msg)

        self._ifu_center_file = ifu_center_file

        self._read_ifu(ifu_center_file)
        if dither_file is None:
            self.dither = dither.EmptyDither()
        else:
            self.dither = dither.ParseDither(dither_file)
        self._read_fextract(fextract)

    def _read_ifu(self, ifu_center_file):
        """
        Read the ifu center file
        Parameters
        ----------
        ifu_center_file: string
            file containing the fiber number to fiber position mapping
        """
        with open(ifu_center_file, 'r') as f:
            # get the fiber diameter and fiber separation
            f = ft.skip_comments(f)
            line = f.readline()
            self.fiber_d, self.fiber_sep = [float(i) for i in line.split()]
            # get the number of fibers in the x and y direction
            f = ft.skip_comments(f)
            line = f.readline()
            self.nfibx, self.nfiby = [int(i) for i in line.split()]
            # get from the rest of the file:
            # the fiber position (second and third column)
            # target unit spectrograph (L or R) (fourth column)
            # target fiber within the spectrograph (fifth column)j
            # relative throughput (sixth column)
            f = ft.skip_comments(f)
            f = self._read_ifu_map(f)

    def _read_ifu_map(self, f):
        """
        Reads and store the remaining part of the file. Each row is expected to
        be like:
        ID        x ["]       y ["]    channel  fiber number        throughput
                                                on spectrograph
        0001      -22.88      -24.24   L (or R) 0001                1.000

        The first column is ignored, the number of L or R is counted, the x, y
        and fiber numbers are saved in lists stored in dictionaries with L or R
        as keys. The throughput is used as check. Missing fibers are indicated
        by negative fiber numbers or non integer values (like 'nan', '-', etc)
        A ValueError is raised if a fiber number is positive and the throughput
        zero
        Parameters
        ----------
        f: file object
        output
        ------
        f: file object
            moved to the next non comment line
        """
        # start the dictionaries
        self.xifu, self.yifu = defaultdict(list), defaultdict(list)
        self.n_fibers = defaultdict(int)
        self.fib_number = defaultdict(list)
        self.throughput = defaultdict(list)

        for line in f:
            if line.startswith('#'):
                continue
            _x, _y, _channel, _fib_n, _t = line.split()[1:6]
            # convert the fiber number to integer. If fails, means that the
            # fiber is broken
            try:
                _fib_n = int(_fib_n)
            except ValueError:
                continue

            if _fib_n > 0:
                if float(_t) < 0.01:  # zero or less
                    msg = 'In the fiber mapping file there is at least one'
                    msg += ' fiber with positive fiber number and 0 throughput'
                    msg += '. What should I do?'
                    raise ValueError(msg)
                else:
                    self.n_fibers[_channel] += 1
                    self.xifu[_channel].append(float(_x))
                    self.yifu[_channel].append(float(_y))
                    # As python indexing is 0 based, subtract 1 from the fiber
                    # number
                    self.fib_number[_channel].append(_fib_n - 1)
                    self.throughput[_channel].append(float(_t))

    def _read_fextract(self, fextract):
        n_channels = len(self.xifu.keys())
        n_dithers = len(self.dx.keys())
        n_shots = n_channels * n_dithers

        # the fiber extracted file names are saved into a dictionary with key
        # like: L_D1
        key = "{ch}_{d}"
        dfextract = {}

        if fextract is None:  # get the file names from the basename
            fetemplate = "Fe{bn}_{ch}.fits"
            for ch, (d, bn) in it.product(self.xifu.keys(), self.dx.item()):
                fextract[key.format(ch=ch, d=d)] = fetemplate.format(ch=ch,
                                                                     bn=bn)
        else:  # the file name is provided
            if len(fextract) != n_shots:
                msg = "The number of fiber extracted files is different from"
                msg += " {} ({} channels and {} dithers)"
                raise ValueError(msg.format(n_shots, len(self.xifu.keys()),
                                            len(self.dx.keys())))
            for fe in fextract:
                header = fits.getheader(fe)
                ch = header['CCDPOS'].strip()
                d = "D{0:d}".format(header['DITHER'])
                dfextract[key.format(ch=ch, d=d)] = fe

        # and now read and save the content of the fiber extracted files and
        # reconstruct the full IFU image
        self._reconstruct(dfextract)

    def _reconstruct(self, dfextract):
        """
        Read the fiber extracted files and creates a set of three lists for x,
        y and flux.
        Parameters
        ----------
        dfextract: dictionary
            name of the fiber extracted file
        """
        self.x, self.y = np.array([[], []], dtype=float)
        self.flux, self.header = [], []
        key = "{ch}_{d}"  # template for key of dfextract

        for ch, d in it.product(self.xifu.keys(), self.dither.dx.keys()):
            # get the correct values of x and y
            self.x = np.concatenate([self.x, self.xpos(ch, d)])
            self.y = np.concatenate([self.y, self.ypos(ch, d)])

            # read the fiber extracted file, order the fibers and save the
            # necessary keys into self.h
            fib_numbs = self.fib_number[ch]
            with fits.open(dfextract[key.format(ch=ch, d=d)]) as hdu:
                h = hdu[0].header
                data = hdu[0].data
                # if the number of fiber from the fiber extracted file is
                # different from the number of fibers, something wrong
                if data.shape[0] != len(fib_numbs):
                    msg = "The number of rows in file '{}' does not agree"
                    msg += "with the number of active fibers from file '{}'"
                    raise IndexError(msg.format(hdu.filename(),
                                                self._ifu_center_file))
                self.flux.append(data[fib_numbs, :])  # reorder the fibers
                # get the header keywords needed to get the index at a given
                # wavelength
                self.header.append({k: h.get(k) for k in ["CRVAL1", "CDELT1"]})

    def xpos(self, channel, dither):
        """
        get the position for the x *dither* in *channel*
        Parameters
        ----------
        channel: string
            name of the channel [L, R]
        dither: string
            name of the dither [D1, D2, ..]
        output
        ------
        xpos: ndarray
            x position of the fibers for the given channel and dither
        """
        return np.array(self.xifu[channel]) + self.dither.dx[dither]

    def ypos(self, channel, dither):
        """
        get the position for the y *dither* in *channel*
        Parameters
        ----------
        channel: string
            name of the channel [L, R]
        dither: string
            name of the dither [D1, D2, ..]
        output
        ------
        ypos: ndarray
            y position of the fibers for the given channel and dither
        """
        return np.array(self.yifu[channel]) + self.dither.dy[dither]

    def reconstruct(self, wmin=None, wmax=None):
        """
        Returns the reconstructed IFU with the flux computed between
        [wmin, wmax]
        wmin, wmax: float
            min and max wavelength to use. If *None*: use the min and/or max
            from the file
        output
        ------
        x, y: 1d arrays
            x and y position of the fibers
        flux: 1d array
            flux of the fibers within *wmin* and *wmax*
        """
        _flux = []
        for f, h in zip(self.flux, self.header):
            _imin = wavelength_to_index(h, wmin)
            _imax = wavelength_to_index(h, wmax)
            _flux.append(f[:, _imin:_imax].sum(axis=1))

        return self.x, self.y, np.concatenate(_flux)
