# Misc python library to support HETDEX software and data analysis
# Copyright (C) 2015, 2017  "The HETDEX collaboration"
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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


def parse_fits_region(region):
    """
    Convert a FITS region string with a format [x1:x2,y1:y2], or
    x1:x2,y1:y2 into an list.

    Parameters
    ----------
    region : str
        The input region string

    Returns
    -------
    list
        List of region parameters

    Examples
    --------

    .. testsetup:: *

        from pyhetdex.tools.files.fits_tools import parse_fits_region

    >>> parse_fits_region('[1:100,2:200]')
    [1, 100, 2, 200]
    """

    req_chars = [':', ',']

    for c in req_chars:
        if c not in region:
            raise ValueError('%s does not match expected format!' % region)

    region = region.strip()

    if region[0] == '[':
        region = region[1:]

    if region[-1] == ']':
        region = region[:-1]

    lims = []
    for dim in region.split(','):
        lims += [int(l) for l in dim.split(':')]

    return lims
