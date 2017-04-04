from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__version__ = '$Id$'


def count_lines(ios):
    """Count the lines in a open file. After counting resets the file position
    to the original one

    Parameters
    ----------
    ios: file object

    Returns
    -------
    lines: int
        number of lines
    """
    currpos = ios.tell()
    lines = 0
    ios.seek(0)

    for _ in ios:
        lines += 1

    ios.seek(currpos)
    return lines


def eat_to_char(ios, c):
    """Advance the file position one character at a time until the desired one
    is found.

    Parameters
    ----------
    ios: file object
    c : character
        single character to find

    Returns
    -------
    ch : character
        character found or last character if not found
    """
    ch = ios.read(1)
    while (ch != c and ch != ''):
        ch = ios.read(1)
    return ch


def eat_to_blockstart(ios):
    """Advance the file position to the first non empty character after a ``[``

    Parameters
    ----------
    ios: file object

    Returns
    -------
    ch : character
        first non empty character
    """
    # First find next '['
    ch = eat_to_char(ios, '[')
    # Then find end of [[[ block
    while (ch != ' ' and ch != ''):
        ch = ios.read(1)
    return ch


def read_to_char(ios, c, skipnewline=True):
    """Read the file until the desired character is found.

    Parameters
    ----------
    ios: file object
    c : character
        single character to find
    skipnewline : bool, optional
        if ``True`` converts new lines to empty spaces

    Returns
    -------
    result : string
        all the read content until ``c`` excluded
    """
    result = ''
    ch = ios.read(1)
    while (ch != c and ch != ''):
        if skipnewline and (ch == '\n'):
            ch = ' '
        result += ch
        ch = ios.read(1)
    return result


def skip_commentlines(ios):
    """Reads one line at a time and returns the first non-empty or non-comment

    Parameters
    ----------
    ios: file object

    Returns
    -------
    line : string
    """
    line = ios.readline()

    if line == '':  # readline returns an empty string when reaching EOF
        return line

    # Clean leading spaces
    line = line.lstrip()
    if len(line):
        if line[0] == '#':
            return skip_commentlines(ios)
    else:  # Skip empty lines
        return skip_commentlines(ios)
    return line


def duplicates(l):
    """Search for duplicates

    Parameters
    ----------
    l : iterable
        iterable and sortable object in which search for duplicates

    Returns
    -------
    list
        sorted list of duplicate items in ``l``
    """
    return list(_duplicates(l))


def _duplicates(l):
    i = j = object()
    for k in sorted(l):
        if i != j == k:
            yield k
        i, j = j, k


def unique(seq, idfun=None):
    """Order preserving unique algorithm

    .. todo::

        see if it makes sense to use :func:`numpy.unique`

    Parameters
    ----------
    seq : iterable
        sequence to order
    idfun : callable
        function to call for the ordering (??)

    Returns
    -------
    result : list
        unique elements
    """
    # order preserving
    if idfun is None:
        def idfun(x):
            return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker in seen:
            continue
        seen[marker] = 1
        result.append(item)
    return result
