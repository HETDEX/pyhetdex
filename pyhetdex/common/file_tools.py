"""
Module containing file manipulation functions
"""

from __future__ import absolute_import

import os


def skip_comments(f):
    """
    Skip commented lines and returns the file at the start of the first
    line without any
    Parameters
    ----------
    f: file object
    output
    ------
    f: file object
        moved to the next non comment line
    """
    pos = f.tell()
    for l in f:
        if l.startswith('#'):
            pos += len(l)
        else:
            break
    f.seek(pos)
    return f


def prefix_filename(path, prefix):
    """
    Split the file name from its path, prepend the *prefix* to the file name
    and join it back
    Parameters
    ----------
    path: string
        file path and name
    prefix: string
        string to prepend
    output
    ------
    path: string
        path with the new file name
    """
    path, fname = os.path.split(path)
    return os.path.join(path, prefix + fname)
