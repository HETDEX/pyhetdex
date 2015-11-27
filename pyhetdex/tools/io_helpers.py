from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__version__ = '$Id$'


def count_lines(ios):
    """
    count the lines in a open file. After counting resets the file position to
    the original one
    Parameters
    ----------
    ios: file object
    output
    ------
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
    ch = ios.read(1)
    while (ch != c and ch != ''):
        ch = ios.read(1)
    return ch


def eat_to_blockstart(ios):
    # First find next '['
    ch = eat_to_char(ios, '[')
    # Then find end of [[[ block
    while (ch != ' ' and ch != ''):
        ch = ios.read(1)
    return ch


def read_to_char(ios, c, skipnewline=True):
    result = ''
    ch = ios.read(1)
    while (ch != c and ch != ''):
        if skipnewline and (ch == '\n'):
            ch = ' '
        result += ch
        ch = ios.read(1)
    return result


def skip_commentlines(ios):
    line = ios.readline().lstrip()
    if len(line):
        if line[0] == '#':
            return skip_commentlines(ios)
    else:  # Skip empty lines
        return skip_commentlines(ios)
    return line


def duplicates(l):
    return list(_duplicates(l))


def _duplicates(l):
    i = j = object()
    for k in sorted(l):
        if i != j == k:
            yield k
        i, j = j, k


def unique(seq, idfun=None):
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

