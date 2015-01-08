"""
Module containing file manipulation functions
"""

from __future__ import absolute_import

import os


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
