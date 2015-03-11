"""
tests for pyhetdex.tools.files.file_tools
"""
from __future__ import print_function, absolute_import

import os
import subprocess
try:  # python 3
    from subprocess import DEVNULL
except ImportError:  # python 2
    DEVNULL = open(os.devnull, 'wb')

import nose.tools as nt

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
    nt.assert_equal(fout, expected)


class Test_scan_files(object):
    """Test the scanning of files. Results compared with shell commands"""

    @classmethod
    def setup_class(cls):
        "setup the class"
        cls.test_dir = os.path.dirname(__file__)
        return cls

    def _len_list(self, *args, **kwargs):
        """Returns the number of elements found by scan_files with the give
        args and kwargs
        """
        return len(list(ft.scan_files(self.test_dir, *args, **kwargs)))

    def _find_files(self, options=[], exclude_dirs=[]):
        """Use shell ``find path -type f`` command to get a list of files to
        compare with the output of ft.scan_files. Returns the number of files

        ``options`` is a list of string with the options to pass to ``find``.
        ``exclude_dirs`` exclude some directory
        """
        command = ['find', self.test_dir, '-type', 'f']
        command.extend(options)
        output = subprocess.check_output(command, stderr=DEVNULL,
                                         universal_newlines=True)
        output = output.splitlines()
        return len(output)

    def test_scan_files(self):
        """scan all files"""
        flist = self._len_list()
        find_list = self._find_files()
        nt.assert_equal(flist, find_list)

    def test_scan_files_norecursive(self):
        """scan all files, no recursive"""
        flist = self._len_list(recursive=False)
        find_list = self._find_files(options=['-maxdepth', '1'])
        nt.assert_equal(flist, find_list)

        # print(list(ft.scan_files(os.path.dirname(__file__),
        #         exclude=['__*', '*pyc', ".??*"])))

    def test_more_tests(self):
        "more tests needed"
        assert False
