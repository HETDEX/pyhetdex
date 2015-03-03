"""Modules that provides utilities related with the sky background

.. moduleauthor:: Francesco Montesano <montefra@mpe.mpg.de>

The main products are:

* :func:`~fe_sky_subtraction`: sky subtraction from fiber extracted frames
* :func:`~fe_sky_background`: estimate the sky background from a file
* :func:`~hdu_fe_sky_background`: estimate the sky background (the content of
  the file is passed)

"""

from __future__ import absolute_import

from astropy.io import fits
from astropy.stats import sigma_clip
import numpy as np

from pyhetdex.tools.files.fits_tools import wavelength_to_index
from pyhetdex.tools.files.file_tools import prefix_filename


# Execute the sky subtraction on the fiber extracted files. The credit for the
# original implementation go to Maximilian Fabricius.
def fe_sky_subtraction(fname, sig=2.5, iters=None, wmin=None, wmax=None,
                       width=20, prefix='S', skyprefix='Sky',
                       output_both=True):
    """Perform the sky subtraction from a fiber extracted frame

    Parameters
    ----------
    fname : string
        name of the fits file to process
    sig : float, optional
        number of standard deviations to use for the clipping limit
    iters  : int or `None`, optional
        number of iterations to perform clipping for, or `None` to clip
        until convergence is achieved (i.e. continue until the last
        iteration clips nothing).
    wmin, wmax : floats, optional
        maximum and minimum wavelength in Armstrong to use for the sigma
        clipping. Converted to indices using the 'CRVAL1' and 'CDELT1' keyword
        in the header of the fits file. If None the minimum and/or maximum of
        the range used
    width : int, optional
        width of the moving window used to estimate the sky background
    prefix : string, optional
        prefix of the sky subtracted file
    skyprefix : string, optional
        prefix of the sky file
    output_both : bool, optional
        save both sky and sky subtracted frames, instead of the latter alone
    """

    with fits.open(fname) as hdulist:
        header = hdulist[0].header
        data = hdulist[0].data

        # get the index of the input wavelengths
        imin = wavelength_to_index(header, wmin)
        imax = wavelength_to_index(header, wmax)

        # take the median along the fibers within the give wavelength range
        median_data = np.median(data[:, imin:imax], axis=1)
        # and get the inverse of the mask from the sigma clipping
        clip_mask = np.logical_not(sigma_clip(median_data, sig=sig,
                                              iters=iters,
                                              cenfunc=np.ma.median).mask)

        # construct the sky frame
        sky = np.empty_like(data)
        for i, _ in enumerate(clip_mask):
            win_mask = moving_window(clip_mask, i, width=width)
            sky[i, :] = np.median(data[win_mask, :], axis=0)

        # save the sky subtracted file
        hdulist[0].data = data - sky
        hdulist.writeto(prefix_filename(fname, prefix), clobber=True)

        if output_both:  # save the sky file
            hdulist[0].data = sky
            hdulist.writeto(prefix_filename(fname, skyprefix), clobber=True)


# estimate the sky background from fiber extracted files
def fe_sky_background(fname, **kwargs):
    """Estimate the sky background as the (sigma clipped) median of medians
    within the required wavelengths and fiber number boundaries.

    The input is read from `fname`. The keyword arguments are passed to
    :func:`~hdu_fe_sky_background`

    Parameters
    ----------
    fname : string
        file to average
    sig : None or float, optional
        if not None, ignore fibers with signal outside *sig* standard deviation
    iters  : int or `None`, optional
        number of iterations to perform clipping for, or `None` to clip
        until convergence is achieved (i.e. continue until the last
        iteration clips nothing).
    wmin, wmax : float, optional
        minimum and maximum wavelength to consider for the average
    wmin, wmax : floats, optional
        maximum and minimum wavelength in Armstrong to use for the estimate.
        Converted to indices using the 'CRVAL1' and 'CDELT1' keyword in the
        header of the fits file. If None the minimum and/or maximum of the
        range used
    fibmin, fibmax : float, optional
        minimum and maximum fiber number to consider

    Returns
    -------
    median : float
        average
    n_fibs : int
        number of fibers used for the final median
    """
    with fits.open(fname) as hdu:
        header = hdu[0].header
        data = hdu[0].data
        return hdu_fe_sky_background(data, header, **kwargs)


def hdu_fe_sky_background(data, header, sig=2.5, iters=None, wmin=None,
                          wmax=None, fibmin=None, fibmax=None):
    """
    Estimate the sky background as the (sigma clipped) median of medians
    within the required wavelengths and fiber number boundaries

    Parameters
    ----------
    data : numpy ndarray
        data of the fits image
    header : astropy.io.fits.Header instance
        header of the fits image
    sig : None or float, optional
        if not None, ignore fibers with signal outside *sig* standard deviation
    iters  : int or `None`, optional
        number of iterations to perform clipping for, or `None` to clip
        until convergence is achieved (i.e. continue until the last
        iteration clips nothing).
    wmin, wmax : float, optional
        minimum and maximum wavelength to consider for the average
    wmin, wmax : floats, optional
        maximum and minimum wavelength in Armstrong to use for the estimate.
        Converted to indices using the 'CRVAL1' and 'CDELT1' keyword in the
        header of the fits file. If None the minimum and/or maximum of the
        range used
    fibmin, fibmax : float, optional
        minimum and maximum fiber number to consider

    Returns
    -------
    median : float
        average
    n_fibs : int
        number of fibers used for the final median
    """
    # get the index of the input wavelengths
    imin = wavelength_to_index(header, wmin)
    imax = wavelength_to_index(header, wmax)
    data = data[fibmin:fibmax, imin:imax]

    if sig is not None:
        median_data = np.median(data, axis=1)
        clip_mask = np.logical_not(sigma_clip(median_data, sig=sig,
                                              iters=iters,
                                              cenfunc=np.ma.median).mask)
        data = data[clip_mask, :]

    median = np.median(np.median(data, axis=1))
    return median, data.shape[0]


# helpers
def moving_window(mask, cindex, width=20):
    """Modify the mask to exclude rows outside the mask

    Parameters
    ----------
    mask : 1d array of bool
        mask across with the window moves
    cindex : int
        central index of the window
    width : int, optional
        maximum width of the window. Edges are not wrapped around

    Returns
    -------
    window_mask : 1d array of bool
        *mask* with all the elements outside the window set to False
    """
    imin = max(0, cindex - width//2)  # lower bound
    imax = min(len(mask)-1, cindex + width//2)  # lower bound

    indx_out = list(range(imin)) + list(range(imax, len(mask)))

    window_mask = mask.copy()
    window_mask[indx_out] = False
    return window_mask
