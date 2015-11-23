"""Reconstruct the IFU

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import itertools as it
import os

from astropy.io import fits
import astropy.stats as stats
import numpy as np

from pyhetdex.tools.files.fits_tools import wavelength_to_index
from pyhetdex.het import ifu_centers, dither as dith
import pyhetdex.cure.distortion as distortion


class ReconstructError(Exception):
    """Generic reconstruction error"""
    pass


class ReconstructIndexError(ReconstructError, IndexError):
    """Error for miss-matching the number of fibers in the ifu center files and
    the fiber extracted ones"""


class ReconstructIOError(ReconstructError, IOError):
    """Error when the name and/or number fiber extracted file names is not
    correct"""
    pass


class ReconstructValueError(ReconstructError, ValueError):
    """Errors for wrong combinations of input parameters in
    :class:`~ReconstructedIFU` or :meth:`~ReconstructedIFU.from_files`"""
    pass


# TODO: account for illumination weights and fiber throughput

class ReconstructedIFU(object):
    r"""Reconstructed IFU head image from the fiber extracted frames given the
    ``ifu_center`` and the ``dither``.

    Parameters
    ----------
    ifu_center : instance of :class:`~pyhetdex.het.ifu_centers.IFUCenter`
        fiber number to fiber position mapping
    dither : instance child of :class:`~pyhetdex.het.dither._BaseDither`
        dither relative position, illumination, image quality
    fextract : None or list of fits files, optional
        * if None the list of files is inferred from
          :attr:`dither.basename`;
        * if not None must have ``ndither`` x ``nchannels`` elements. The
          channel name and dither number are extracted from the ``CCDPOS`` and
          the ``DITHER`` header keywords
    fe_prefix : string, optional
        when getting the names from the dither file, prepend ``fe_prefix`` to
        the ``basename``

    Attributes
    ----------
    ifu_center
    dither
    x, y : 1-dimensional arrays
        x and y position of the fibers
    flux : list of 2-dimensional arrays
        each element is the content of one fiber extracted file
    header : list of dictionaries
        each element contains the ``CRVAL1`` and ``CDELT1`` keywords :value
        pairs from the headers of the fiber extracted files; used to determine
        the wavelength range in  :meth:`~reconstruct`

    Raises
    ------
    ReconstructValueError
        if an empty dither is passed and ``fextract`` is ``None``
    ReconstructIOError
        if the number and/or number of fiber extracted frames is not correct;
        raised by :meth:`~_fedict`
    ReconstructIndexError
        if the number of fibers from the fiber extracted files and from the ifu
        center files do not match; raised by :meth:`~_reconstruct`
    """

    def __init__(self, ifu_center, dither, fextract=None,
                 fe_prefix=""):
        if isinstance(dither, dith.EmptyDither) and fextract is None:
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
                   fe_prefix=""):
        """
        Read and parse the file

        Parameters
        ----------
        ifu_center_file : string
            file containing the fiber number to fiber position mapping
        dither_file : string, optional
            file containing the dither relative position. If not given, a singe
            dither is assumed
        fextract : None or list of fits files, optional
            if None the list of files is inferred from the second column
            of the ``dither_file``;
            if not None must have ``ndither`` x ``nchannels`` elements. The
            channel name and dither number are extracted from the ``CCDPOS``
            and the ``DITHER`` header keywords
        fe_prefix : string, optional
            when getting the names from the dither file, prepend ``fe_prefix``
            to the ``basename``

        Raises
        ------
        ReconstructValueError
            if both ``dither_file`` and ``fextract`` are ``None``
        ReconstructValueError, ReconstructIOError
            as in :class:`~ReconstructedIFU`

        Notes
        -----
            if ``dither_file`` is None, ``fextract`` must contain a number of
            files equal to the number of channels (2)
        """
        if dither_file is None and fextract is None:
            msg = "dither_file and/or fextract must be provided"
            raise ReconstructValueError(msg)

        _ifu_center = ifu_centers.IFUCenter(ifu_center_file)
        if dither_file is None:
            _dither = dith.EmptyDither()
        else:
            _dither = dith.ParseDither(dither_file)

        return cls(_ifu_center, _dither, fextract=fextract,
                   fe_prefix=fe_prefix)

    def _fedict(self, fextract):
        """
        Organize the fiber extracted file names into a dictionary

        Parameters
        ----------
        fextract : None or list of string
            If None get the file names from the dither, otherwise from the
            *fextract* list

        Returns
        -------
        dfextract : dict
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
                if k in dfextract:
                    msg = "The file '{}' is for the same dither".format(fe)
                    msg += " and channel as file '{}'".format(dfextract[k])
                    raise ReconstructIOError(msg)
                else:
                    try:
                        all_keys.remove(k)
                    except ValueError:
                        msg = ("The file '{}' is for an unknown combination of"
                               " dither ({}) and channel ({}). One of {}"
                               " expected".format(fe, d, ch,
                                                  ", ".join(all_keys)))
                        raise ReconstructIOError(msg)

                dfextract[k] = fe

        return dfextract

    def _reconstruct(self, dfextract):
        """
        Read the fiber extracted files and creates a set of three lists for x,
        y and flux.

        Parameters
        ----------
        dfextract : dictionary
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
                    raise ReconstructIndexError(msg)
                self.flux.append(data[fib_numbs, :])  # order the fibers
                # get the header keywords needed to get the index at a given
                # wavelength
                self.header.append({k: h.get(k) for k in ["CRVAL1", "CDELT1"]})

    def xpos(self, channel, dither):
        """get the position for the x *dither* in *channel*

        Parameters
        ----------
        channel : string
            name of the channel [L, R]
        dither : string
            name of the dither [D1, D2, ..]

        Returns
        -------
        ndarray
            x position of the fibers for the given channel and dither
        """
        return np.array(self.ifu_center.xifu[channel]) + self.dither.dx[dither]

    def ypos(self, channel, dither):
        """get the position for the y *dither* in *channel*

        Parameters
        ----------
        channel : string
            name of the channel [L, R]
        dither : string
            name of the dither [D1, D2, ..]

        Returns
        -------
        ndarray
            y position of the fibers for the given channel and dither
        """
        return np.array(self.ifu_center.yifu[channel]) + self.dither.dy[dither]

    def reconstruct(self, wmin=None, wmax=None):
        """
        Returns the reconstructed IFU with the flux computed between
        [``wmin``, ``wmax``]

        Parameters
        ----------
        wmin, wmax : float, optional
            min and max wavelength to use. If ``None``: use the min and/or max
            from the file

        Returns
        -------
        x, y : 1d arrays
            x and y position of the fibers
        flux : 1d array
            flux of the fibers within ``wmin`` and ``wmax``
        """
        _flux = []
        for f, h in zip(self.flux, self.header):
            _imin = wavelength_to_index(h, wmin)
            _imax = wavelength_to_index(h, wmax)
            _flux.append(f[:, _imin:_imax].sum(axis=1))

        return self.x, self.y, np.concatenate(_flux)


class QuickReconstructedIFU(object):
    """Quick reconstructed IFU head image from a set of frames given the
    ``ifu_center`` and some reference distortion files.

    Parameters
    ----------
    ifu_center : instance of :class:`~pyhetdex.het.ifu_centers.IFUCenter`
        fiber number to fiber position mapping
    files : string
        Basefilename of the image to be reconstructed, or a tuple of three
        images to reconstruct a complete dither.
    dist_l, dist_r : string
        Distortion file for the left and right spectrograph; at least one of
        them must be provided
    pixscale : float, optional
        pixel scale

    Attributes
    ----------
    ifu_center : :class:`~pyhetdex.het.ifu_centers.IFUCenter`
        parsed ``ifu_center`` file
    dx, dy : tuples
        relative shifts of the dithers
    pscale : float
        pixel scale
    img : 2d numpy array
        reconstructed image

    Raises
    ------
    ReconstructValueError
        if an empty dither is passed and ``fextract`` is ``None``
    ReconstructIOError
        if the number and/or number of fiber extracted frames is not correct;
        raised by :meth:`~_fedict`
    ReconstructIndexError
        if the number of fibers from the fiber extracted files and from the ifu
        center files do not match; raised by :meth:`~_reconstruct`
    """

    def __init__(self, ifu_center, files, dist_r=None,
                 dist_l=None, pixscale=0.25):
        if not ifu_center:
            raise ReconstructValueError('An IFU center file is needed to'
                                        ' quickreconstruct an image')

        self.ifu_center = ifu_centers.IFUCenter(ifu_center)
        if not dist_r and not dist_l:
            raise ReconstructValueError('A distortion is needed to'
                                        ' quickreconstruct an image')

        self.dists = {'L': None, 'R': None}
        if dist_l:
            self.dists['L'] = distortion.Distortion(dist_l)
        if dist_r:
            self.dists['R'] = distortion.Distortion(dist_r)

        self.files = files

        self.dx = (0, -1.27, -1.27)
        self.dy = (0, 0.73, -0.73)

        self._pscale = pixscale

        self.maxx = (max((max(self.ifu_center.xifu['L']),
                          max(self.ifu_center.xifu['R']))) +
                     max(self.dx) + self.ifu_center.fiber_d/2.)
        self.minx = (min((min(self.ifu_center.xifu['L']),
                          min(self.ifu_center.xifu['R']))) +
                     min(self.dx) - self.ifu_center.fiber_d/2.)

        self.maxy = (max((max(self.ifu_center.yifu['L']),
                         max(self.ifu_center.yifu['R']))) +
                     max(self.dy) + self.ifu_center.fiber_d/2.)
        self.miny = (min((min(self.ifu_center.yifu['L']),
                          min(self.ifu_center.yifu['R']))) +
                     min(self.dy) - self.ifu_center.fiber_d/2.)

    @property
    def pscale(self):
        """Pixel scale

        .. warning::
            changing the pixel scale with invalidate the reconstructed
            image
        """
        return self._pscale

    @pscale.setter
    def pscale(self, pixscale):
        self._pscale = pixscale
        try:
            del self.img
        except AttributeError:
            pass

    def reconstruct(self, subtract_overscan=True):
        """
        Read the fiber extracted files and creates a set of three lists for x,
        y and flux.

        Parameters
        ----------
        subtract_overscan : bool
            If the overscan region is still present in the image,
            subtract the bias level, calculated from the overscan
            region of the image.

        Returns
        -------
        img : nd-array
            reconstructed image; it is also stored in the :attr:`img`
            attribute
        """

        xc = np.array([], dtype=float)
        yc = np.array([], dtype=float)
        flx = np.array([], dtype=float)

        ifuid = None

        for img in self.files:  # Loop over all input file

            dx, dy = 0, 0  # Default offset value
            f_offset = 0  # Python arrays start at 0, FITS files at 1...

            with fits.open(img) as hdu:

                print('Working on ', img)

                h = hdu[0].header
                data = hdu[0].data.transpose()

                if not ifuid:
                    ifuid = h['IFUID']
                elif ifuid != h['IFUID']:
                    print('WARNING: %s if from a different IFU, skipping it!')
                    continue
                ccdpos = h['CCDPOS']

                D = self.dists[ccdpos]
                if not D:
                    raise ReconstructValueError('No distortion given for ' +
                                                ccdpos + ' spectrograph')

                if h['NAXIS2'] < 1500:
                    if h['CCDHALF'] == 'U':
                        f_offset = 1032  # FIXME This should come from header
                        ampstr = 'upper amplifier'
                    else:
                        ampstr = 'lower amplifier'
                else:
                    ampstr = 'full'

                if h['NAXIS1'] > 1032 and subtract_overscan:
                    print('Removing bias calculated from overscan region')
                    bias = self._get_overscan(data, h['BIASSEC'])
                    data = data-bias

                dither_step = int(h['DITHER'])-1

                print('This is a %s image for the %s spectrograph '
                      'in dither step %d' % (ampstr, ccdpos, dither_step+1))

                dx = self.dx[dither_step]
                dy = self.dy[dither_step]

                center_x = np.round(data.shape[0]/2)

                for f in range(self.ifu_center.n_fibers[ccdpos]):
                    # fib = f+1
                    fy_f = D.map_xf_y(516, D.reference_f_.data[f]) - f_offset
                    fy = np.floor(fy_f)
                    fy_d = fy_f - fy
                    if fy < 0 or fy > data.shape[1]:
                        continue

                    flx = np.append(flx, np.sum(data[center_x-20:center_x+20,
                                                     fy-1:fy+2]) +
                                    np.sum(data[center_x-20:center_x+20,
                                                fy-2:fy-1]*(1.-fy_d)) +
                                    np.sum(data[center_x-20:center_x+20,
                                                fy+2:fy+3]*(fy_d)))

                    # Include the dither offset
                    xc = np.append(xc, self.ifu_center.xifu[ccdpos][f] + dx)
                    yc = np.append(yc, self.ifu_center.yifu[ccdpos][f] + dy)

        # Now loop over the output image and add the flux from all fibers

        fr_2 = self.ifu_center.fiber_d ** 2 / 4.

        self._create_empty_image()
        it = np.nditer(self.img, flags=['multi_index'], op_flags=['writeonly'])

        while not it.finished:
            px = self.minx + it.multi_index[0] * self.pscale
            py = self.miny + it.multi_index[1] * self.pscale

            dx = xc - px
            dy = yc - py

            dd = (dx*dx + dy*dy)
            it[0] = np.sum(flx[dd < fr_2])
            it.iternext()

    def write(self, filename):
        """Write the reconstructed image to file ``filename`` as using the fits
        format

        Parameters
        ----------
        filename : string
            name of the output fits file
        """
        try:
            outimg = fits.PrimaryHDU(self.img)
        except AttributeError:
            raise ReconstructError("Make sure to run the ``reconstruct``"
                                   " method to create the image before saving"
                                   " it")
        outimg.writeto(filename, clobber=True)

    def _section_to_list(self, sec):
        """
        Convert a header section string of the form [x1:x2,y1:y2]
        to a list of integers

        Parameters
        ----------
        sec : str
            The header section string
        """
        return [int(i) for i in sec.replace('[', '').replace(']', '').
                replace(':', ',').split(',')]

    def _get_overscan(self, img, biassec):
        r"""Extract the sigma clipped mean of the overscan region

        Parameters
        ----------
        img : instance of :class:`numpy.array`
            Input image data
        biassec : list
            List or tuple with the ranges of the bias section.
            Use :func:_section_to_list to convert the header
            BIASSEC keyword to a python list
        """

        biasreg = self._section_to_list(biassec)
        return np.mean(stats.sigma_clip(img[biasreg[0]:biasreg[1], ]))

    def _create_empty_image(self):
        """Find the number of pixels x and y and create empty images"""
        nx = (self.maxx - self.minx) / self.pscale
        ny = (self.maxy - self.miny) / self.pscale
        self.img = np.zeros((nx, ny))
        # self.weight = np.ones((nx, ny))


def argument_parser(argv=None):
    """Parse the command line"""
    import argparse

    # Parse user input
    description = """Reconstruct the IFU image from a list of fits images."""

    parser = argparse.ArgumentParser(description=description,
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('ifucen', help="""Name of the IFUcen file""")
    parser.add_argument('files', nargs='+', help="""The input images""")

    parser.add_argument('-o', '--outfile', help="""Name of a file to output""",
                        default='reconstruct.fits')
    parser.add_argument('-l', '--ldist', help="""Name of the distortion file for the
                        left spectrograph; at least one of '%(dest)s' or
                        'rdist' must be provided""")
    parser.add_argument('-r', '--rdist', help="""Name of the distortion file for the
                        right spectrograph""")
    parser.add_argument('-s', '--scale', help="""Scale of the pixels in the
                        reconstructed image""", default=0.3, type=float)

    return parser.parse_args(argv)


def create_quick_reconstruction(argv=None):
    """Entry point for the executable running the quick reconstruction of the
    IFU reconstruction image

    Parameters
    ----------
    argv : list of strings
        if not provided sys.argv is used
    """
    args = argument_parser(argv=argv)

    # create the shot object
    recon = QuickReconstructedIFU(args.ifucen, args.files, dist_r=args.rdist,
                                  dist_l=args.ldist, pixscale=args.scale)

    recon.reconstruct(subtract_overscan=True)
    recon.write(args.outfile)
