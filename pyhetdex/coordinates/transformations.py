"""Coordinate transformation

Created on Oct 4, 2011

.. moduleauthor: Maximilian Fabricius <>

Note
----
    These routines are taken from http://astlib.sourceforge.net/

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
    https://ned.ipac.caltech.edu/forms/calculator.html.
    The values obtained with the function disagrees at the 7th digit level with
    the value from ``ned`` (should we consider it a failure?). Using only the
    hour, the values is wrong, according to ``ned``

    :func:`~calcAngSepDeg`: the test fails. Where it is possible to get a
    reference value?
    http://cads.iiap.res.in/tools/angularSeparation and 
    http://www.asdc.asi.it/dist.html gives very different answers, and none of
    them agrees with the output of the function
"""

import numpy


# -----------------------------------------------------------------------------
def hms2decimal(RAString, delimiter=":"):
    """Converts a delimited string of ``Hours:Minutes:Seconds`` format into
    decimal degrees.

    Parameters
    ----------
    RAString: string
        coordinate string in ``H:M:S`` format
    delimiter: string
        delimiter character in ``RAString``

    Returns
    -------
    RADeg: float
        coordinate in decimal degrees
    """
    # is it in HH:MM:SS format?
    if delimiter == "":
        RABits = str(RAString).split()
    else:
        RABits = str(RAString).split(delimiter)

    if len(RABits) > 1:
        RAHDecimal = float(RABits[0])
        if len(RABits) > 1:
            RAHDecimal = RAHDecimal + (float(RABits[1]) / 60.0)
        if len(RABits) > 2:
            RAHDecimal = RAHDecimal + (float(RABits[2]) / 3600.0)
        RADeg = (RAHDecimal / 24.0) * 360.0
    else:
        RADeg = float(RAString)

    return RADeg


# -----------------------------------------------------------------------------
def dms2decimal(decString, delimiter=":"):
    """Converts a delimited string of ``Degrees:Minutes:Seconds`` format into
    decimal degrees.

    Parameters
    ----------
    decString: string
        coordinate string in ``D:M:S`` format
    delimiter: string
        delimiter character in decString

    Returns
    -------
    decDeg: float
        coordinate in decimal degrees
    """
    # is it in DD:MM:SS format?
    if delimiter == "":
        decBits = str(decString).split()
    else:
        decBits = str(decString).split(delimiter)
    if len(decBits) > 1:
        decDeg = float(decBits[0])
        if decBits[0].find("-") != -1:
            if len(decBits) > 1:
                decDeg = decDeg-(float(decBits[1]) / 60.0)
            if len(decBits) > 2:
                decDeg = decDeg-(float(decBits[2]) / 3600.0)
        else:
            if len(decBits) > 1:
                decDeg = decDeg+(float(decBits[1]) / 60.0)
            if len(decBits) > 2:
                decDeg = decDeg+(float(decBits[2]) / 3600.0)
    else:
        decDeg = float(decString)

    return decDeg


# -----------------------------------------------------------------------------
def decimal2hms(RADeg, delimiter=":"):
    """Converts decimal degrees to string in ``Hours:Minutes:Seconds`` format
    with user specified delimiter.

    Parameters
    ----------
    RADeg: float
        coordinate in decimal degrees
    delimiter: string
        delimiter character in returned string

    Returns
    -------
    string
        coordinate string in ``H:M:S`` format
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


# -----------------------------------------------------------------------------
def decimal2dms(decDeg, delimiter=":"):
    """Converts decimal degrees to string in ``Degrees:Minutes:Seconds`` format
    with user specified delimiter.

    Parameters
    ----------
    decDeg: float
        coordinate in decimal degrees
    delimiter: string
        delimiter character in returned string

    Returns
    -------
    string
        coordinate string in ``D:M:S`` format
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


# -----------------------------------------------------------------------------
def calcAngSepDeg(RADeg1, decDeg1, RADeg2, decDeg2):
    """Calculates the angular separation of two positions on the sky in decimal
    degrees, assuming a tangent plane projection.

    Parameters
    ----------
    RADeg1: float
        R.A. in decimal degrees for position 1
    decDeg1: float
        dec. in decimal degrees for position 1
    RADeg2: float or numpy array
        R.A. in decimal degrees for position 2
    decDeg2: float or numpy array
        dec. in decimal degrees for position 2

    Returns
    -------
    r: float or numpy array
        angular separation in decimal degrees

    Note
    ----
    so separation has to be less than 90 deg
    """
    cRA = numpy.radians(RADeg1)
    cDec = numpy.radians(decDeg1)

    gRA = numpy.radians(RADeg2)
    gDec = numpy.radians(decDeg2)

    cosC = (numpy.sin(gDec) * numpy.sin(cDec))
    cosC += (numpy.cos(gDec) * numpy.cos(cDec) * numpy.cos(gRA - cRA))
    x = (numpy.cos(cDec) * numpy.sin(gRA - cRA)) / cosC
    y = ((numpy.cos(gDec) * numpy.sin(cDec)) - (numpy.sin(gDec) *
         numpy.cos(cDec) * numpy.cos(gRA - cRA))) / cosC
    r = numpy.degrees(numpy.sqrt(x * x + y * y))

    return r
