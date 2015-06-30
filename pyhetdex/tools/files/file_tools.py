""" Module containing file manipulation functions

.. testsetup:: *

    from pyhetdex.tools.files.file_tools import wildcards_to_regex
    from pyhetdex.tools.files.file_tools import prefix_filename

.. moduleauthor: Francesco Montesano <montefra@mpe.mpg.de>
"""

from __future__ import absolute_import

import fnmatch
import os
import re

import six


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
    '/path/to/new_file.dat'
    """
    path, fname = os.path.split(path)
    return os.path.join(path, prefix + fname)


def wildcards_to_regex(wildcards, re_compile=True):
    """Convert shell wildcard to regex

    If ``wildcards`` is None, a match-nothing regex is used
    If ``wildcards`` is a list, the resulting regex are concatenated with ``|``
    (or)

    Examples
    --------

    >>> wildcards_to_regex("[0-9]*fits")  # doctest: +SKIP
    "re.compile('[0-9].*fits\\\\Z(?ms)', re.MULTILINE|re.DOTALL)"
    >>> wildcards_to_regex("[0-9]*fits", re_compile=False)
    '[0-9].*fits\\\\Z(?ms)'
    >>> wildcards_to_regex(None, re_compile=False)
    'a^'
    >>> wildcards_to_regex(["[0-3]*fits", "[5-9]*fits"], re_compile=False)
    '[0-3].*fits\\\\Z(?ms)|[5-9].*fits\\\\Z(?ms)'

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
    elif isinstance(wildcards, six.string_types):
        regex = fnmatch.translate(wildcards)
    else:
        regex = r'|'.join(fnmatch.translate(wc) for wc in wildcards)

    if re_compile:
        return re.compile(regex)
    else:
        return regex


def scan_files(path, matches='*', exclude=None, exclude_dirs=None,
               recursive=True, followlinks=True):
    """Generator that search and serves files.

    Parameters
    ----------
    path : string
        path to search
    matches : string or list of strings, optional
        Unix shell-style wildcards to filter; done on the full path+filename
    exclude : string or list of strings, optional
        Unix shell-style wildcards to exclude files; done on the full
        path+filename
    exclude_dirs : string or list of strings, optional
        Unix shell-style wildcards to exclude subdirectories
    recursive : bool, optional
        search files recursively into ``path``
    followlinks : bool, optional
        follow symlinks

    Returns
    -------
    fn : string
        name of the file (it's an iterator, not a return)

    .. todo::
        use ``Yields`` instead of ``Returns`` when the numpydoc 0.6 update will
        be available

    Yields
    ------
    fn : string
        name of the file

    """
    # convert ``matches``, ``exclude`` and ``exclude_dirs`` into compiled regex
    matches = wildcards_to_regex(matches)
    exclude = wildcards_to_regex(exclude)
    exclude_dirs = wildcards_to_regex(exclude_dirs)

    for pathname, dirnames, filenames in os.walk(path, topdown=True,
                                                 followlinks=followlinks):
        if not recursive:  # don't walk subdirectories
            dirnames[:] = ''
        # removes directories
        to_remove = []
        for d in dirnames:
            if exclude_dirs.search(d) is not None:
                to_remove.append(d)
        for tr in to_remove:
            dirnames.remove(tr)

        for fn in filenames:
            fname = os.path.join(pathname, fn)
            if (matches.match(fname) is not None and
                    exclude.match(fname) is None):
                yield fname


def scan_dirs(path, matches='*', exclude=None, recursive=True,
              followlinks=True):
    """Generator that searches for and serves directories

    Parameters
    ----------
    path : string
        path to search
    matches : string or list of strings, optional
        Unix shell-style wildcards to filter
    exclude : string or list of strings, optional
        Unix shell-style wildcards to exclude directories
    recursive : bool, optional
        search files recursively into ``path``
    followlinks : bool, optional
        follow symlinks

    Returns
    -------
    dirname : string
        name of the directory (it's an iterator, not a return)

    Yields
    ------
    dirname : string
        name of the directory

    .. todo::
        remove returns when the numpydoc 0.6 update will be available
    """
    # convert ``matches``, ``exclude`` into compiled regex
    matches = wildcards_to_regex(matches)
    exclude = wildcards_to_regex(exclude)

    for pathname, dirnames, _ in os.walk(path, topdown=True,
                                         followlinks=followlinks):
        for dn in dirnames:
            dirname = os.path.join(pathname, dn)
            if (matches.match(dirname) is not None and
                    exclude.match(dirname) is None):
                yield dirname

        if not recursive:  # don't walk subdirectories
            dirnames[:] = ''
