"""
tests for pyhetdex.tools.files.file_tools
"""
from __future__ import print_function, absolute_import

import os
import re
import subprocess
try:  # python 3
    from subprocess import DEVNULL
except ImportError:  # python 2
    DEVNULL = open(os.devnull, 'wb')

import pyhetdex.tools.files.file_tools as ft


def test_prefix_filename():
    """
    test the insertion of a prefix in front of the file name
    """
    fnames = ["/abs/path/to/file.txt",
              "../../rel/path/file.dat",
              "nopath.file"
              ]
    prefix = "test_"
    expected_fnames = ["/abs/path/to/test_file.txt",
                       "../../rel/path/test_file.dat",
                       "test_nopath.file"
                       ]
    for ifn, ofn in zip(fnames, expected_fnames):
        yield _prefix_filename, ifn, prefix, ofn


def _prefix_filename(fname, prefix, expected):
    """
    Run the test of the single files
    """
    fout = ft.prefix_filename(fname, prefix)
    assert fout == expected


def test_wildcards_to_regex():
    """Convert shell wildcards to regex"""
    wildcards = ["[0-9]*fits", None, ["[0-3]*fits", "[5-9]*fits"]]
    expected = [r'[0-9].*fits\Z(?ms)', r'a^',
                r'[0-3].*fits\Z(?ms)|[5-9].*fits\Z(?ms)']

    for wc, ex in zip(wildcards, expected):
        yield _wildcards_to_regex, wc, ex, False
        yield _wildcards_to_regex, wc, re.compile(ex), True


def _wildcards_to_regex(wildcards, expected_re, re_compile=True):
    """Actually do the comparison"""
    r = ft.wildcards_to_regex(wildcards, re_compile=re_compile)
    assert r == expected_re


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
        return sorted(list(ft.scan_files(self.test_dir, *args, **kwargs)))

    def _find_files(self, options=[]):
        """Use shell ``find path -type f`` command to get a list of files to
        compare with the output of ft.scan_files. Returns the sorted list

        ``options`` is a list of string with the options to pass to ``find``.
        """
        command = ['find', self.test_dir, '-type', 'f']
        command.extend(options)
        output = subprocess.check_output(command, stderr=DEVNULL,
                                         universal_newlines=True)
        output = output.splitlines()
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
        flist = self._scan_files(exclude_dirs=['data', '__pycache__'])
        find_list = self._find_files(options=['-maxdepth', '1'])
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
        cls.test_dir = os.path.join(os.path.dirname(__file__), "..",
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
