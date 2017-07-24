""" Module containing file manipulation functions

.. testsetup:: *

    from pyhetdex.tools.files.file_tools import wildcards_to_regex
    from pyhetdex.tools.files.file_tools import prefix_filename

.. moduleauthor: Francesco Montesano <montefra@mpe.mpg.de>
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import fnmatch
import glob
import os
import re

import six


class RegexCompileFail(re.error):
    """Error raised when the compilation fails"""
    pass


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

    >>> print(prefix_filename('/path/to/file.dat', 'new_'))
    /path/to/new_file.dat
    """
    path, fname = os.path.split(path)
    return os.path.join(path, prefix + fname)


def wildcards_to_regex(wildcards, re_compile=True, is_regex=False):
    """Convert shell wildcard to regex, if ``is_regex`` is ``False``

    If ``wildcards`` is None, a match-nothing regex is used
    If ``wildcards`` is a list, the resulting regex are concatenated with ``|``
    (or)

    Examples
    --------

    >>> print(type(wildcards_to_regex("[0-9]*fits")))  # doctest: +ELLIPSIS
    <... '_sre.SRE_Pattern'>
    >>> print(wildcards_to_regex("[0-9]*fits",
    ...       re_compile=False))  # doctest: +SKIP
    [0-9].*fits\Z(?ms)
    >>> print(wildcards_to_regex(None, re_compile=False))
    a^
    >>> print(wildcards_to_regex(["[0-3]*fits", "[5-9]*fits"],
    ...       re_compile=False))  # doctest: +SKIP
    [0-3].*fits\Z(?ms)|[5-9].*fits\Z(?ms)

    Parameters
    ----------
    wildcards : None, string or list of strings
        shell wildcards
    re_compile : bool, optional
        if true compile the regex before returning
    is_regex : bool, optional
        interpret the input as a regex

    Returns
    -------
    regex : string or :class:`re.RegexObject`
        resulting regex

    Raises
    ------

    """
    if wildcards is None:
        regex = r'a^'
    elif isinstance(wildcards, six.string_types):
        if is_regex:
            regex = wildcards
        else:
            regex = fnmatch.translate(wildcards)
    else:
        if is_regex:
            regex = r'|'.join(wildcards)
        else:
            regex = r'|'.join(fnmatch.translate(wc) for wc in wildcards)

    if re_compile:
        try:
            return re.compile(regex)
        except re.error as e:
            msg = ("Compiling the regex expression '{}' deriving from '{}'"
                   " failed because of {}".format(regex, wildcards, e))
            six.raise_from(RegexCompileFail(msg), e)
    else:
        return regex


def scan_files(path, matches='*', exclude=None, exclude_dirs=None,
               recursive=True, followlinks=True, is_matches_regex=False,
               is_exclude_regex=False, is_exclude_dirs_regex=False):
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
    is_matches_regex, is_exclude_regex, is_exclude_dirs_regex : bool, optional
        mark the corresponding options as a regex pattern instead of unix shell
        pattern with possible wildcards

    Yields
    ------
    fn : string
        name of the file
    """
    # convert ``matches``, ``exclude`` and ``exclude_dirs`` into compiled regex
    matches = wildcards_to_regex(matches, is_regex=is_matches_regex)
    exclude = wildcards_to_regex(exclude, is_regex=is_exclude_regex)
    exclude_dirs = wildcards_to_regex(exclude_dirs,
                                      is_regex=is_exclude_dirs_regex)

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
              followlinks=True, is_matches_regex=False,
              is_exclude_regex=False):
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
    is_matches_regex, is_exclude_regex : bool, optional
        mark the corresponding options as a regex pattern instead of unix shell
        pattern with possible wildcards

    Yields
    ------
    dirname : string
        name of the directory
    """
    # convert ``matches``, ``exclude`` into compiled regex
    matches = wildcards_to_regex(matches, is_regex=is_matches_regex)
    exclude = wildcards_to_regex(exclude, is_regex=is_exclude_regex)

    for pathname, dirnames, _ in os.walk(path, topdown=True,
                                         followlinks=followlinks):
        for dn in dirnames:
            dirname = os.path.join(pathname, dn)
            if (matches.match(dirname) is not None and
                    exclude.match(dirname) is None):
                yield dirname

        if not recursive:  # don't walk subdirectories
            dirnames[:] = ''


class FileNameRotator(object):
    """Given a group of file name templates, creates new file names using a
    common counter that avoid file name clashes. The file templates follow the
    standard python string format syntax and expect **only one empty**. The
    file name is joined with the path

    Examples
    --------
    >>> tmp = getfixture('tmpdir')  # get a temp directory from pytest
    >>> fnr = FileNameRotator(tmp.strpath, log1='file_{}.log',
    ...                       log2='other_{}.log')
    >>> print(os.path.basename(fnr.log1))
    file_0.log
    >>> print(os.path.basename(fnr.log2))
    other_0.log

    Parameters
    ----------
    path : string
        path to search for files
    keep : int, optional
        if not negative, files with the counter less than (max_number -
        keep) are removed
    kwargs : keyword options
        template of the files; they are added as attributes to the instance

    Raises
    ------
    AttributeError
        if the name associated to one file is already in use
    ValueError
        if it's not possible to format the template
    """
    def __init__(self, path, keep=-1, **kwargs):
        self._path = path
        self._validate(kwargs)
        self._re_counter = r'(\d+?)'

        dfiles_templates = {k: os.path.join(path, fn)
                            for k, fn in kwargs.items()}

        counter = self._n_files(dfiles_templates.values())
        dfiles, counter = self._create_file_names(dfiles_templates, counter)
        self._add_file_names(dfiles)

        if keep >= 0:
            self._remove_older(dfiles_templates.values(), counter, keep)

    def _validate(self, dfiles):
        """Check that none of the keys is already used and that the file
        templates contain the '{}' string

        Parameters
        ----------
        dfiles : dictionary
            keys and file name templates

        Raises
        ------
        AttributeError
            if the name associated to one file is already in use
        ValueError
            if it's not possible to format the template
        """
        for k, v in six.iteritems(dfiles):
            if hasattr(self, k):
                raise AttributeError("Can't set attribute {}".format(k))
            try:
                v.format('*')
                v.format(1)
                if v == v.format(1):
                    raise KeyError()
            except KeyError:
                raise ValueError("The file template must support being"
                                 " formatted with a number of ``*``")

    def _n_files(self, files):
        """Find the number that the next files should have.

        Parameters
        ----------
        files : list
            list of file name templates

        Returns
        -------
        file_counter : int
            counter for the new files
        """
        file_counter = -1

        for fn_tempate in files:
            pattern = re.compile(fn_tempate.format(self._re_counter))
            for fn in glob.glob(fn_tempate.format('*')):
                counter = int(pattern.findall(fn)[0])
                file_counter = max(file_counter, counter)

        return file_counter + 1

    def _create_file_names(self, dfiles, n_files):
        """Create the file names starting the counter from ``n_files``. If any
        of the created files exist, increase the counter and retry. Once all
        file names are found, touch them.

        Parameters
        ----------
        dfiles : dictionary
            keys and file name templates
        n_files : int
            starting point for the counter; if any of the files exists, the
            counter is increased

        Returns
        -------
        fnames : dictionary
            file names with the counter replaced
        counter : int
            actual counter used
        """
        keep_going = True
        n_files -= 1

        while keep_going:
            n_files += 1
            fnames = {k: v.format(n_files) for k, v in six.iteritems(dfiles)}
            keep_going = any([os.path.exists(v) for v in fnames.values()])

        # touch the files
        for v in fnames.values():
            with open(v, mode='w'):
                pass

        return fnames, n_files

    def _remove_older(self, files, counter, keep):
        '''All the files with a counter smaller than ``counter - keep`` are
        removed.

        Parameters
        ----------
        files : list
            file name templates
        counter : int
            number used to create the new file
        keep : int
            number of files to keep beside the newly created one
        '''
        max_counter = counter - keep

        for fn_tempate in files:
            pattern = re.compile(fn_tempate.format(self._re_counter))
            for fn in glob.glob(fn_tempate.format('*')):
                if int(pattern.findall(fn)[0]) < max_counter:
                    os.remove(fn)

    def _add_file_names(self, dfiles):
        """Add the created file names as instance attributes

        Parameters
        ----------
        dfiles : dictionary
            keys and file names
        """
        for k, v in six.iteritems(dfiles):
            setattr(self, k, v)
