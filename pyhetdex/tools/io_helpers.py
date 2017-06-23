from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import pkg_resources
import re
import six
import textwrap as tw

try:  # python 2 override raw_input
    input = raw_input
except NameError:  # python 3 is already fine
    pass

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


def ask_yes_no(message):
    '''Ask the user ``message`` and expect ``y`` or ``n`` as answer.

    The string `` (y/[n])`` is appended to the ``message``.
    EOF (``ctrl+D``) and empty string are interpreted as ``n``

    Parameters
    ----------
    message : string
        message to print to screen

    Returns
    -------
    is_yes : bool
        whether the answer is ``y``
    '''
    is_yes = False
    msg = message + ' (y/[n]) '
    while True:
        try:
            answer = input(msg)
            if not answer:
                answer = 'n'
            if answer.lower() == 'y':
                is_yes = True
                break
            elif answer.lower() == 'n':
                break
            else:
                continue
        except EOFError:
            print()
            break

    return is_yes


def decode(bytes_):
    """In python 3 decodes bytes into string, in python 2 returns the
    input

    Parameters
    ----------
    bytes_ : byte type
        string to encode

    Returns
    -------
    string
    """
    if six.PY3 and isinstance(bytes_, six.binary_type):
        return bytes_.decode()
    else:
        return bytes_


def get_resource_file(name, filename):
    '''Get the file from the package using `setuptools resource access
    <https://setuptools.readthedocs.io/en/latest/pkg_resources.html#basic-resource-access>`_
    and decode it.

    Parameters
    ----------
    name : string
        name of the package. Typically is the ``__name__`` variable of the
        module calling the function
    filename : string
        name of the file relative to ``name``

    Returns
    -------
    file_content : string
        content of the file
    '''
    file_content = pkg_resources.resource_string(name, filename)
    return decode(file_content)


def copy_resources(name, flist, target_dir, reldir='.', backup=False,
                   force=False, replace_func=None, verbose=False):
    """Copy the given list of resource files.

    If one of the files already exists on the destination one of the following
    cases happens:

    * the user is asked whether she/he wants to replace the file;
    * if ``force`` is ``True``: the file is replaced without asking;
    * if ``backup`` is ``True``: the destination file is copied to a new file,
      to which name ``".bkp"`` is appended, and then replaced; overridden by
      ``force``

    Parameters
    ----------
    name : string
        name of the package. Typically is the ``__name__`` variable of the
        module calling the function
    flist : list of strings
        list of files to copy relative to ``name``
    target_dir : string
        directory where to copy the files
    reldir : string, optional
        if the files to copy are into a ``reldir`` directory with respect to
        ``name``, this will path will be removed form the destination path.
        E.g. if ``reldir = "static"`` directory and ``flist =
        ["static/my_file.cfg", ]`` and the file will be copied into
        ``"target_dir/my_file.cfg"``. If ``reldir`` is not given the file will
        be copied into ``"target_dir/static/my_file.cfg"``. ``reldir`` must be
        at the beginning of the file names or will be ignored.
    backup : bool, optional
        existing files are backed-up before copying the new ones
    force : bool, optional
        force overwriting if the file already exists; override backup
    replace_func : callable, optional
        callable that accepts a string (the resource file) and return an other
        string that will be then written to file; useful e.g. to replace
        placeholders in the files
    verbose : bool, optional
        activate verbose printing

    Returns
    -------
    written_files, non_written_files, backed_up_files : list of strings
        name of the files that has been written, not written or backed-up
    """
    written_files = []
    non_written_files = []
    backed_up_files = []

    for filename in flist:
        # if the file is relative, mark it as such
        if reldir and filename.startswith(reldir):
            rel_filename = os.path.relpath(filename, start=reldir)
        else:
            rel_filename = filename

        dir_, file_ = os.path.split(rel_filename)
        if dir_:  # create the target directory
            _target_dir = os.path.join(target_dir, dir_)
        else:
            _target_dir = target_dir

        try:  # try to make the target directory
            os.mkdir(_target_dir)
            if verbose:
                print("Directory '{}' created".format(dir_))
        except OSError:
            pass

        ofile = os.path.join(_target_dir, file_)
        ofile_exists = os.path.exists(ofile)

        if ofile_exists:
            overwrite = False
            if force:
                overwrite = True
            elif backup:
                bkp = ofile + '.bkp'
                os.rename(ofile, bkp)
                backed_up_files.append(rel_filename)
                overwrite = True
            else:
                msg = "Do you want to overwrite file '{}'?"
                overwrite = ask_yes_no(msg.format(rel_filename))

            if not overwrite:
                non_written_files.append(rel_filename)
                continue

        ifile = get_resource_file(name, filename)
        if replace_func:
            ifile = replace_func(ifile)

        with open(ofile, 'w') as of:
            of.write(ifile)
        written_files.append(rel_filename)

    return written_files, non_written_files, backed_up_files


def print_list(header, list_):
    '''If ``list_`` is not empty, print it after header and indented
    accordingly.

    >>> printed = print_list('test header: ', ['entry1', 'entry2', 'entry3',
    ...                                        'entry4', 'entry5', 'entry6',
    ...                                        'entry7', 'entry8'])
    test header: entry1, entry2, entry3, entry4, entry5, entry6, entry7,
                 entry8
    >>> printed
    True

    Parameters
    ----------
    header : string
        header to put in the first line and to use to indent the subsequent
        lines. It can contain ANSI escape characters for, e.g. coloring
    list_ : list of strings
        the list is joined with commas and printed after header

    Returns
    -------
    printed : bool
        whether something has been printed
    '''
    printed = False
    if list_:
        escaped_header = re.sub(r'(\x9b|\x1b\[)[0-?]*[ -\/]*[@-~]', '', header,
                                flags=re.IGNORECASE)
        msg = tw.fill(", ".join(list_),
                      initial_indent=header,
                      subsequent_indent=" "*len(escaped_header))
        print(msg)
        printed = True
    return printed
