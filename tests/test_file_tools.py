"""
tests for pyhetdex.common.file_tools
"""

import nose.tools as nt

import pyhetdex.common.file_tools as ft

def test_prefix_filename():
    """
    test the insertion of a prefix in front of the file name
    """
    fnames = [ "/abs/path/to/file.txt"
             , "../../rel/path/file.dat"
             , "nopath.file"
             ]
    prefix = "test_"
    expected_fnames = [ "/abs/path/to/test_file.txt"
                      , "../../rel/path/test_file.dat"
                      , "test_nopath.file"
                      ]
    for ifn, ofn in zip(fnames, expected_fnames):
        yield _prefix_filename, ifn, prefix, ofn


def _prefix_filename(fname, prefix, expected):
    """
    Run the test of the single files
    """
    fout = ft.prefix_filename(fname, prefix)
    nt.assert_equal(fout, expected)



