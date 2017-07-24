"""
tests for pyhetdex.tools.files.file_tools
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import re
import subprocess
try:  # python 3
    from subprocess import DEVNULL
except ImportError:  # python 2
    DEVNULL = open(os.devnull, 'wb')
import sys

import six
import pytest

import pyhetdex.tools.files.file_tools as ft

parametrize = pytest.mark.parametrize


skip_greater_py36 = pytest.mark.skipif(sys.version_info >= (3, 6),
                                       reason='Valid for python >= 3.6')
skip_smaller_py36 = pytest.mark.skipif(sys.version_info < (3, 6),
                                       reason='Valid for python < 3.6')


@parametrize('text, next_line',
             [('no comment', 'no comment'),
              ('#test\n#cat\nno comment', 'no comment'),
              ('#test\n#cat\n', ''),
              ])
def test_skip_comments(text, next_line):
    '''Skipping comments'''
    f = six.StringIO(text)

    f = ft.skip_comments(f)

    line = f.readline()
    assert line == next_line


@parametrize('infname, prefix, outfname',
             (["/abs/path/to/file.txt", "test_", "/abs/path/to/test_file.txt"],
              ["../../rel/path/file.dat", "test_",
               "../../rel/path/test_file.dat"],
              ["nopath.file", "test_", "test_nopath.file"]
              ))
def test_prefix_filename(infname, prefix, outfname):
    "test the insertion of a prefix in front of the file name"
    fout = ft.prefix_filename(infname, prefix)
    assert fout == outfname


@parametrize('re_compile', [False, True])
@parametrize('wildcard, regex, is_regex',
             (skip_greater_py36(['[0-9]*fits', r'[0-9].*fits\Z(?ms)', False]),
              skip_smaller_py36(['[0-9]*fits', r'(?s:[0-9].*fits)\Z', False]),
              [None, r'a^', False], [None, r'a^', True],
              skip_greater_py36([["[0-3]*fits", "[5-9]*fits"],
                                 r'[0-3].*fits\Z(?ms)|[5-9].*fits\Z(?ms)',
                                 False]),
              skip_smaller_py36([["[0-3]*fits", "[5-9]*fits"],
                                 r'(?s:[0-3].*fits)\Z|(?s:[5-9].*fits)\Z',
                                 False]),
              [r'(?:e\.)?jpes[0-9].*fits', r'(?:e\.)?jpes[0-9].*fits', True],
              [[r'.*some\d{2}.?', r'thing\d{2}.?'],
               r'.*some\d{2}.?|thing\d{2}.?', True],
              pytest.mark.xfail(reason="Wrong regex",
                                raises=ft.RegexCompileFail)
                               (["*wrong", "*wrong", True])
              ))
def test_wildcards_to_regex(wildcard, regex, is_regex, re_compile):
    """Convert shell wildcards to regex"""
    if wildcard and "wrong" in wildcard and not re_compile:
        pytest.skip("Check only wrong regex compilation")
    r = ft.wildcards_to_regex(wildcard, re_compile=re_compile,
                              is_regex=is_regex)
    if re_compile:
        assert r.pattern == regex
        assert type(r), type(re.compile(".*"))
    else:
        assert r == regex


class Test_scan_files(object):
    """Test the scanning of files. Results compared with shell commands"""

    @classmethod
    def setup_class(cls):
        "setup the class"
        cls.test_dir = os.path.dirname(__file__)
        return cls

    def _scan_files(self, *args, **kwargs):
        """Returns the sorted elements found by scan_files with the give
        args and kwargs
        """
        return sorted(o for o in ft.scan_files(self.test_dir, *args, **kwargs)
                      if '.svn' not in o)

    def _find_files(self, options=[]):
        """Use shell ``find path -type f`` command to get a list of files to
        compare with the output of ft.scan_files. Returns the sorted list

        ``options`` is a list of string with the options to pass to ``find``.
        """
        command = ['find', self.test_dir, '-type', 'f']
        command.extend(options)
        output = subprocess.check_output(command, stderr=DEVNULL,
                                         universal_newlines=True)
        output = [o for o in output.splitlines() if '.svn' not in o]
        return sorted(output)

    def test_scan_files(self):
        """scan all files"""
        flist = self._scan_files()
        find_list = self._find_files()
        assert flist == find_list

    def test_scan_files_norecursive(self):
        """scan all files, no recursive"""
        flist = self._scan_files(recursive=False)
        find_list = self._find_files(options=['-maxdepth', '1'])
        assert flist == find_list

    def test_directory_exclusion(self):
        """exclude directories"""
        flist = self._scan_files(exclude_dirs=['__pycache__', ])
        find_list = self._find_files()
        find_list = [i for i in find_list if '__pycache__' not in i]
        assert flist == find_list

    def test_filter_files(self):
        """Filter only python files"""
        flist = self._scan_files(matches=["*py"])
        find_list = self._find_files(options=['-name', '*py'])
        assert flist == find_list

    def test_exclude_files(self):
        """Exclude python files"""
        flist = self._scan_files(exclude=["*py"])
        find_list = self._find_files(options=['!', '-name', '*py'])
        assert flist == find_list


class Test_scan_dir(object):
    """Test the scanning of directories. Results compared with shell
    commands"""

    @classmethod
    def setup_class(cls):
        "setup the class"
        cls.test_dir = os.path.join(os.path.dirname(__file__), "..", "..",
                                    "pyhetdex")
        return cls

    def _scan_dirs(self, *args, **kwargs):
        """Returns the sorted elements found by scan_dirs with the given
        args and kwargs
        """
        return sorted(list(ft.scan_dirs(self.test_dir, *args, **kwargs)))

    def _find_dirs(self, options=[]):
        """Use shell ``find path -type d`` command to get a list of files to
        compare with the output of ft.scan_dirs. Returns the sorted list of
        directories

        ``options`` is a list of string with the options to pass to ``find``.
        """
        command = ['find', self.test_dir, '-type', 'd']
        command.extend(options)
        output = subprocess.check_output(command, stderr=DEVNULL,
                                         universal_newlines=True)
        output = output.splitlines()
        try:
            output.remove(self.test_dir)
        except ValueError:
            pass
        return sorted(output)

    def test_scan_dirs(self):
        """scan all directories"""
        dlist = self._scan_dirs()
        find_list = self._find_dirs()
        assert dlist == find_list

    def test_scan_dirs_norecursive(self):
        """scan all directories, no recursive"""
        dlist = self._scan_dirs(recursive=False)
        find_list = self._find_dirs(options=['-maxdepth', '1'])
        assert dlist == find_list

    def test_filter_dirs(self):
        """Filter only directory 'tools' """
        dlist = self._scan_dirs(matches=["*tool*"])
        find_list = self._find_dirs(options=['-path', '*tool*'])
        assert dlist == find_list

    def test_directory_exclusion(self):
        """exclude directory 'tools'"""
        dlist = self._scan_dirs(exclude=['*tool*', '*pycache*'])
        find_list = self._find_dirs(options=['!', '-path', '*tool*', '!',
                                             '-path', '*pycache*'])
        assert dlist == find_list


@parametrize('n_times', [1, 2, 5])
@parametrize('keep', [-1, 0, 1, 3])
def test_file_name_rotator(tmpdir, n_times, keep):
    """Test that the rotation of the files works properly, calling it
    n_times"""
    fn = {'file1': 'test_{}.log', 'file2': 'other_{}.log'}
    for i in range(n_times):
        fn_rotator = ft.FileNameRotator(str(tmpdir), keep=keep, **fn)
        assert fn['file1'].format(i) in fn_rotator.file1
        assert fn['file2'].format(i) in fn_rotator.file2

    files = list(tmpdir.visit(fil='*.log'))

    if keep < 0:
        n_left = n_times
    else:
        n_left = min(n_times, keep + 1)

    assert len(files) == 2 * n_left


@pytest.mark.parametrize('fname',
                         ['good_{}.log',
                          pytest.mark.xfail(raises=ValueError, reason='Invalid'
                                            'format of the file name'
                                            'template')('bad.log'),
                          pytest.mark.xfail(raises=ValueError, reason='Invalid'
                                            'format of the file name'
                                            'template')('bad_{:.3f}.log'),
                          ])
def test_file_name_rotator_template(tmpdir, fname):
    fn_rotator = ft.FileNameRotator(tmpdir.strpath, fname=fname)

    assert fname.format(0) in fn_rotator.fname


@pytest.mark.xfail(raises=AttributeError,
                   reason='The attribute already exists')
def test_file_name_rotator_attr_error():
    # subclass rotator to add attribute
    class SubClass(ft.FileNameRotator):
        def extra(self):
            pass

    SubClass('/a/paht', extra="fname")


def test_file_name_rotator_counter(tmpdir):
    """Test that the counter number is always increased"""
    fns = {'file1': 'test_{}.log', 'file2': 'other_{}.log'}
    for fn in fns.values():
        tmpdir.ensure(fn.format(10))
        break

    fn_rotator = ft.FileNameRotator(str(tmpdir), **fns)

    for k, v in fns.items():
        assert v.format(11) in getattr(fn_rotator, k)
