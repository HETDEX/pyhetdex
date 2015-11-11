"""Coordinate transformations

Created on Oct 4, 2011

.. moduleauthor: Maximilian Fabricius <>

Notes
-----
    These routines are taken from `astlib <http://astlib.sourceforge.net/>`_

.. todo::
    :func:`~decimal2dms`: the two external if branches are almost exact
    repetitions. Solution: save the sign of the input ``decDeg`` variable;
    convert the input as it were positive, the add the sign before returning.
    Also most of the internal if branches are either superfluous or repetitions
    that can be factored out.

    Also :func:`~decimal2hms` show a fair amount of repetitions, in big part
    similar to the above function.

    Once the refactoring is finished, the tests should be updated to cover all
    the branches.

    :func:`~hms2decimal` tests fail: all the input values in the
    ``setup_class`` method are obtained with
    `ned calculator <https://ned.ipac.caltech.edu/forms/calculator.html>`_.
    The values obtained with the function disagrees at the 7th digit level with
    the value from ``ned`` (should we consider it a failure?). Using only the
    hour, the values is wrong.

    Should we use `astropy.coordinates
    <http://astropy.readthedocs.org/en/v1.0/coordinates/index.html>`_ instead
    of this implementation?


.. testsetup:: *

    from pyhetdex.coordinates.transformations import *
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def hms2decimal(ra_string, delimiter=":"):
    """Converts a delimited string of ``Hours:Minutes:Seconds`` format into
    decimal degrees.

    Parameters
    ----------
    ra_string : string
        coordinate string in ``H :M:S`` format
    delimiter : string
        delimiter character in ``RAString``

    Returns
    -------
    ra_deg : float
        coordinate in decimal degrees

    Examples
    --------

    .. doctest::

        >>> hms2decimal("02:41:43.033")
        40.42930416666667
    """
    # is it in HH:MM:SS format?
    if delimiter == "":
        ra_split = str(ra_string).split()
    else:
        ra_split = str(ra_string).split(delimiter)

    if len(ra_split) > 1:
        ra_decimal = float(ra_split[0])
        if len(ra_split) > 1:
            ra_decimal = ra_decimal + (float(ra_split[1]) / 60.0)
        if len(ra_split) > 2:
            ra_decimal = ra_decimal + (float(ra_split[2]) / 3600.0)
        ra_deg = (ra_decimal / 24.0) * 360.0
    else:
        ra_deg = float(ra_string)

    return ra_deg


def dms2decimal(dec_string, delimiter=":"):
    """Converts a delimited string of ``Degrees:Minutes:Seconds`` format into
    decimal degrees.

    Parameters
    ----------
    dec_string : string
        coordinate string in ``D :M:S`` format
    delimiter : string
        delimiter character in ``dec_string``

    Returns
    -------
    dec_deg : float
        coordinate in decimal degrees

    Examples
    --------
    .. doctest::

        >>> dms2decimal("+40:25:45.50")
        40.42930555555555
    """
    # is it in DD:MM:SS format?
    if delimiter == "":
        dec_split = str(dec_string).split()
    else:
        dec_split = str(dec_string).split(delimiter)
    if len(dec_split) > 1:
        dec_deg = float(dec_split[0])
        if dec_split[0].find("-") != -1:
            if len(dec_split) > 1:
                dec_deg = dec_deg-(float(dec_split[1]) / 60.0)
            if len(dec_split) > 2:
                dec_deg = dec_deg-(float(dec_split[2]) / 3600.0)
        else:
            if len(dec_split) > 1:
                dec_deg = dec_deg+(float(dec_split[1]) / 60.0)
            if len(dec_split) > 2:
                dec_deg = dec_deg+(float(dec_split[2]) / 3600.0)
    else:
        dec_deg = float(dec_string)

    return dec_deg


def decimal2hms(RADeg, delimiter=":"):
    """Converts decimal degrees to string in ``Hours:Minutes:Seconds`` format
    with user specified delimiter.

    Parameters
    ----------
    RADeg : float
        coordinate in decimal degrees
    delimiter : string
        delimiter character in returned string

    Returns
    -------
    string
        coordinate string in ``Hour:Minutes:Seconds`` format

    Examples
    --------
    .. doctest::

        >>> print(decimal2hms(40.42930556))
        02:41:43.033
    """
    hours = (RADeg / 360.0) * 24
    if hours < 10 and hours >= 1:
        sHours = "0" + str(hours)[0]
    elif hours >= 10:
        sHours = str(hours)[:2]
    elif hours < 1:
        sHours = "00"

    if str(hours).find(".") == -1:
        mins = float(hours) * 60.0
    else:
        mins = float(str(hours)[str(hours).index("."):]) * 60.0
    if mins < 10 and mins >= 1:
        sMins = "0" + str(mins)[:1]
    elif mins >= 10:
        sMins = str(mins)[:2]
    elif mins < 1:
        sMins = "00"

    secs = (hours - (float(sHours) + float(sMins) / 60.0)) * 3600.0
    if secs < 10 and secs > 0.001:
        sSecs = "0" + str(secs)[:str(secs).find(".") + 4]
    elif secs < 0.0001:
        sSecs = "00.001"
    else:
        sSecs = str(secs)[:str(secs).find(".") + 4]
    if len(sSecs) < 5:
        sSecs = sSecs + "00"  # So all to 3dp

    if float(sSecs) == 60.000:
        sSecs = "00.00"
        sMins = str(int(sMins) + 1)
    if int(sMins) == 60:
        sMins = "00"

    return sHours + delimiter + sMins + delimiter + sSecs


def decimal2dms(decDeg, delimiter=":"):
    """Converts decimal degrees to string in ``Degrees:Minutes:Seconds`` format
    with user specified delimiter.

    Parameters
    ----------
    decDeg : float
        coordinate in decimal degrees
    delimiter : string
        delimiter character in returned string

    Returns
    -------
    string
        coordinate string in ``D:M:S`` format

    Examples
    --------
    .. doctest::

        >>> print(decimal2dms(40.42930556))
        +40:25:45.50
    """
    # Positive
    if decDeg > 0:
        if decDeg < 10 and decDeg >= 1:
            sDeg = "0" + str(decDeg)[0]
        elif decDeg >= 10:
            sDeg = str(decDeg)[:2]
        elif decDeg < 1:
            sDeg = "00"

        if str(decDeg).find(".") == -1:
            mins = float(decDeg) * 60.0
        else:
            mins = float(str(decDeg)[str(decDeg).index("."):]) * 60
        if mins < 10 and mins >= 1:
            sMins = "0" + str(mins)[:1]
        elif mins >= 10:
            sMins = str(mins)[:2]
        elif mins < 1:
            sMins = "00"

        secs = (decDeg-(float(sDeg) + float(sMins) / 60.0)) * 3600.0
        if secs < 10 and secs > 0:
            sSecs = "0" + str(secs)[:str(secs).find(".") + 3]
        elif secs < 0.001:
            sSecs = "00.00"
        else:
            sSecs = str(secs)[:str(secs).find(".") + 3]
        if len(sSecs) < 5:
            sSecs = sSecs + "0"	 # So all to 2dp

        if float(sSecs) == 60.00:
            sSecs = "00.00"
            sMins = str(int(sMins) + 1)
        if int(sMins) == 60:
            sMins = "00"
            sDeg = str(int(sDeg) + 1)

        return "+" + sDeg + delimiter + sMins + delimiter + sSecs

    else:
        if decDeg > -10 and decDeg <= -1:
            sDeg = "-0" + str(decDeg)[1]
        elif decDeg <= -10:
            sDeg = str(decDeg)[:3]
        elif decDeg > -1:
            sDeg = "-00"

        if str(decDeg).find(".") == -1:
            mins = float(decDeg) * -60.0
        else:
            mins = float(str(decDeg)[str(decDeg).index("."):]) * 60
        if mins < 10 and mins >= 1:
            sMins = "0" + str(mins)[:1]
        elif mins >= 10:
            sMins = str(mins)[:2]
        elif mins < 1:
            sMins = "00"

        secs = (decDeg-(float(sDeg)-float(sMins) / 60.0)) * 3600.0
        if secs > -10 and secs < 0:
            # so don't get minus sign
            sSecs = "0" + str(secs)[1:str(secs).find(".") + 3]
        elif secs > -0.001:
            sSecs = "00.00"
        else:
            sSecs = str(secs)[1:str(secs).find(".") + 3]
        if len(sSecs) < 5:
            sSecs = sSecs + "0"  # So all to 2dp

        if float(sSecs) == 60.00:
            sSecs = "00.00"
            sMins = str(int(sMins) + 1)
        if int(sMins) == 60:
            sMins = "00"
            sDeg = str(int(sDeg)-1)

        return sDeg + delimiter + sMins + delimiter + sSecs
