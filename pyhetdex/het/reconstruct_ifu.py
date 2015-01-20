"""
Reconstruct the IFU
"""

from __future__ import print_function, absolute_import

import itertools as it
import os

from astropy.io import fits
import numpy as np

from pyhetdex.common.fitstools import wavelength_to_index


class RecontructIndexError(IndexError):
    pass


class ReconstructIOError(IOError):
    pass


class ReconstructValueError(ValueError):
    pass


# TODO: account for illumination weights and fiber throughput
class ReconstructedIFU(object):
    """
    Reconstructed IFU head image from the fiber extracted frames given the
    *ifu_center_file* and if any, the *dither_file*.
    """

    def __init__(self, ifu_center, dither, fextract=None,
                 fe_prefix="Fe"):
        """
        Read and parse the file
        Parameters
        ----------
        ifu_center: instance of ifu_centers.IFUCenter
            fiber number to fiber position mapping
        dither: instance of dither._BaseDither
            dither relative position, illumination, image quality
        fextract: None or list of fits files
            if None the list of files is inferred from first or second column
            of the *dither_file*;
            if not None must have *ndither* x *nchannels* elements. The channel
            name and dither number are extracted from the *CCDPOS* and the
            *DITHER* header keywords
        fe_prefix: string
            when getting the names from the dither file, prepend *fe_prefix* to
            the *basename*
        WARNING: *dither_file* and *fextract* cannot be *None* at the same time
        WARNING: if *dither_file* is None, *fextract* must contain a number of
        files equal to the number of channels (2)
        NOTE: should this distinction be moved to factory functions?
        """
        from pyhetdex import het
        if isinstance(dither, het.dither.EmptyDither) and fextract is None:
            msg = "With an empty dither file a fiber extract file name must be"
            msg += " provided"
            raise ReconstructValueError(msg)

        self.ifu_center = ifu_center
        self.dither = dither

        # public attributes, filled in *_reconstruct*
        self.x, self.y = np.array([[], []], dtype=float)
        self.flux, self.header = [], []

        self._fe_prefix = fe_prefix
        # the fiber extracted file names are saved into a dictionary with key
        # like: D1_L
        self._key = "{d}_{ch}"

        self._reconstruct(self._fedict(fextract))

    @classmethod
    def from_files(cls, ifu_center_file, dither_file=None, fextract=None,
                   fe_prefix="Fe"):
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
        fe_prefix: string
            when getting the names from the dither file, prepend *fe_prefix* to
            the *basename*
        WARNING: *dither_file* and *fextract* cannot be *None* at the same time
        WARNING: if *dither_file* is None, *fextract* must contain a number of
        files equal to the number of channels (2)
        NOTE: should this distinction be moved to factory functions?
        """
        if dither_file is None and fextract is None:
            msg = "dither_file and/or fextract must be provided"
            raise ReconstructValueError(msg)

        from pyhetdex import het
        _ifu_center = het.ifu_centers.IFUCenter(ifu_center_file)
        if dither_file is None:
            _dither = het.dither.EmptyDither()
        else:
            _dither = het.dither.ParseDither(dither_file)

        return cls(_ifu_center, _dither, fextract=fextract,
                   fe_prefix=fe_prefix)

    def _fedict(self, fextract):
        """
        Organize the fiber extracted file names into a dictionary
        Parameters
        ----------
        fextract: None or list of string
            If None get the file names from the dither, otherwise from the
            *fextract* list
        output
        ------
        dfextract: dict
            dictionary of fiber extracted frames
        """
        channels = self.ifu_center.channels
        dithers = self.dither.dithers

        n_shots = len(channels) * len(dithers)

        dfextract = {}

        if fextract is None:  # get the file names from the dither file
            fetemplate = os.path.join(self.dither.abspath,
                                      self._fe_prefix + "{bn}_{ch}.fits")
            for ch, (d, bn) in it.product(channels,
                                          self.dither.basename.items()):
                k = self._key.format(ch=ch, d=d)
                dfextract[k] = fetemplate.format(ch=ch, bn=bn)
        else:  # the file names are provided
            if len(fextract) != n_shots:
                msg = "The number of fiber extracted files is different from"
                msg += " {} ({} channels and {} dithers)"
                raise ReconstructIOError(msg.format(n_shots, len(channels),
                                                    len(dithers)))
            # as the fiber extracted files are ordered, pop elements. This way
            # makes sure that all the dithers and channels are represented
            all_keys = [self._key.format(d=d, ch=ch) for d in dithers for ch in
                        channels]
            for fe in fextract:
                header = fits.getheader(fe)
                ch = header['CCDPOS'].strip()
                d = "D{0:d}".format(header['DITHER'])
                k = self._key.format(ch=ch, d=d)
                # check that the files are correct
                try:
                    all_keys.remove(k)
                except ValueError:
                    msg = "The file '{}' is for an unknown combination of"
                    msg += " dither ({}) and channel ({})"
                    raise ReconstructIOError(msg.format(fe, d, ch))
                if k in dfextract:
                    msg = "The file '{}' is for the same dither".format(fe)
                    msg += " and channel as file '{}'".format(dfextract[k])
                    raise ReconstructIOError(msg)

                dfextract[k] = fe

        return dfextract

    def _reconstruct(self, dfextract):
        """
        Read the fiber extracted files and creates a set of three lists for x,
        y and flux.
        Parameters
        ----------
        dfextract: dictionary
            name of the fiber extracted file
        """
        for ch, d in it.product(self.ifu_center.channels, self.dither.dithers):
            # get the correct values of x and y
            self.x = np.concatenate([self.x, self.xpos(ch, d)])
            self.y = np.concatenate([self.y, self.ypos(ch, d)])

            # read the fiber extracted file, order the fibers and save the
            # necessary keys into self.h
            # python starts from 0
            fib_numbs = [fn - 1 for fn in self.ifu_center.fib_number[ch]]

            k = self._key.format(ch=ch, d=d)
            with fits.open(dfextract[k]) as hdu:
                h = hdu[0].header
                data = hdu[0].data
                # if the number of fiber from the fiber extracted file is
                # different from the number of fibers, something wrong
                if data.shape[0] != len(fib_numbs):
                    msg = "The number of rows in file '{0}' ({1:d}) does not"
                    msg += " agree with the number of active fibers from file"
                    msg += " '{2}' ({3:d})"
                    msg = msg.format(hdu.filename(), data.shape[0], 
                                     self.ifu_center.filename, len(fib_numbs))
                    raise RecontructIndexError(msg)
                self.flux.append(data[fib_numbs, :])  # order the fibers
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
        return np.array(self.ifu_center.xifu[channel]) + self.dither.dx[dither]

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
        return np.array(self.ifu_center.yifu[channel]) + self.dither.dy[dither]

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
