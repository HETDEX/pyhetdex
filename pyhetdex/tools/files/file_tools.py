""" Module containing file manipulation functions

.. moduleauthor: Francesco Montesano <montefra@mpe.mpg.de>
"""

from __future__ import absolute_import

import fnmatch
import os
import re

# python 2/3 compatibility
try:  # Python 2
    basestring
except NameError:  # python 3
    basestring = str


def skip_comments(f):
    """Skip commented lines and returns the file at the start of the first line
    without any

    Parameters
    ----------
    f : file object

    Returns
    -------
    f : file object
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
    path : string
        file path and name
    prefix : string
        string to prepend

    Returns
    -------
    string
        path with the new file name

    Examples
    --------

    >>> prefix_filename('/path/to/file.dat', 'new_')
    /path/to/new_file.dat
    """
    path, fname = os.path.split(path)
    return os.path.join(path, prefix + fname)


def _wildcards_to_regex(wildcards, re_compile=True):
    """Convert shell wildcard to regex

    If ``wildcards`` is None, a match-nothing regex is used
    If ``wildcards`` is a list, the resulting regex are concatenated with ``|``
    (or)

    Parameters
    ----------
    wildcards : None, string or list of strings
        shell wildcards
    re_compile : bool, optional
        if true compile the regex before returning

    Returns
    -------
    regex : string or :class:`re.RegexObject`
        resulting regex
    """
    if wildcards is None:
        regex = r'a^'
    elif isinstance(wildcards, basestring):
        regex = fnmatch.translate(wildcards)
    else:
        regex = r'|'.join(fnmatch.translate(wc) for wc in wildcards)

    if re_compile:
        return re.compile(regex)
    else:
        regex


def scan_files(path, matches='*', exclude=None, exclude_dirs=None,
               recursive=True):
    """Generator that search and serves files

    Parameters
    ----------
    path : string
        path to search
    matches : string or list of strings, optional
        Unix shell-style wildcards to filter
    exclude : string or list of strings, optional
        Unix shell-style wildcards to exclude files and subdirectories
    exclude_dirs : string or list of strings, optional
        Unix shell-style wildcards to exclude files and subdirectories
    recursive : bool, optional
        search files recursively into ``path``

    Returns
    -------
    fn: string
        name of the file (it's an iterator, not a return)

    Yields
    ------
    fn: string
        name of the file

    .. todo::
        remove returns when the numpydoc 0.6 update will be available
    """
    # convert ``matches``, ``exclude`` and ``exclude_dirs`` into compiled regex
    matches = _wildcards_to_regex(matches)
    exclude = _wildcards_to_regex(exclude)
    exclude_dirs = _wildcards_to_regex(exclude_dirs)

    for pathname, dirnames, filenames in os.walk(path, topdown=True):
        if not recursive:  # don't walk subdirectories
            dirnames[:] = ''
        # removes directories
        for i, d in enumerate(dirnames):
            if exclude_dirs.search(d) is not None:
                dirnames.remove(d)

        for fn in filenames:
            if matches.match(fn) is not None and exclude.match(fn) is None:
                yield os.path.join(pathname, fn)
