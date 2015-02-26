"""Functions related with fits files

.. moduleauthor:: Francesco Montesano <montefra@mpe.mpg.de>
"""

from __future__ import absolute_import


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

    >>> wavelength_to_index({'CRVAL1': 3500, 'CDELT1': 2}, 4000)
    250
    """
    if wavelength is None:
        return None
    wmin = header["CRVAL1"]
    deltaw = header["CDELT1"]
    i = int(round((wavelength - wmin) / deltaw))
    return i
