"""Functions related with fits files

.. moduleauthor:: Francesco Montesano <montefra@mpe.mpg.de>
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def wavelength_to_index(header, wavelength):
    """
    Using the ``CRVAL1`` and ``CDELT1`` keywords in ``header`` determine the
    index of ``wavelength``

    Parameters
    ----------
    header : dictionary like
        dictionary containing the above keywords
    wavelength : float
        wavelength. If None, return None

    Returns
    -------
    int or None
        index of ``wavelength``

    Examples
    --------

    .. testsetup:: *

        from pyhetdex.tools.files.fits_tools import wavelength_to_index

    >>> wavelength_to_index({'CRVAL1': 3500, 'CDELT1': 2}, 4000)
    250
    """
    if wavelength is None:
        return None
    wmin = header["CRVAL1"]
    deltaw = header["CDELT1"]
    i = (wavelength - wmin) // deltaw
    return i
