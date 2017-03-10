"Test pyhetdex.tools.io_helpers"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pyhetdex.tools.io_helpers as ioh
import pytest


@pytest.yield_fixture
def testfile(request, tmpdir):
    '''Create a test file and returns a file object to read it'''
    fname = tmpdir.mkdir('io').join('test.txt')
    with fname.open('w') as fout:
        # fout = fname.open('w')
        fout.write('# Comment\n')
        fout.write('#!\n')
        fout.write('#\n')
        fout.write('\n')
        fout.write('Test <123>\n')
        fout.write('[ 1 2 3 ]\n')
        # fout.close()

    with fname.open() as fin:
        yield fin


@pytest.yield_fixture
def testfile_nocomments(request, tmpdir):
    '''Create a test file without comment lines
    and returns a file object to read it'''
    fname = tmpdir.mkdir('io').join('test.txt')
    with fname.open('w') as fout:
        # fout = fname.open('w')
        fout.write('Test <123>\n')
        fout.write('[ 1 2 3 ]\n')
        # fout.close()

    with fname.open() as fin:
        yield fin


@pytest.fixture(scope='module')
def testlist():
    'return a list of integers'
    return [1, 1, 1, 2, 1, 3, 2, 1]


class TestIOHelpers(object):

    def test_countlines(self, testfile):
        assert ioh.count_lines(testfile) == 6

    def test_eat_to_char(self, testfile):
        assert ioh.eat_to_char(testfile, '<') == '<'

    def test_eat_to_blockstart(self, testfile):
        assert ioh.eat_to_blockstart(testfile) == ' '

    def test_read_to_char(self, testfile):
        assert ioh.read_to_char(testfile, '!') == '# Comment #'

    def test_read_to_char_noskipnewline(self, testfile):
        assert ioh.read_to_char(testfile, '!', False) == '# Comment\n#'

    def test_skip_comment(self, testfile):
        assert ioh.skip_commentlines(testfile) == 'Test <123>\n'

    def test_skip_comment_no_comment(self, testfile_nocomments):
        assert ioh.skip_commentlines(testfile_nocomments) == 'Test <123>\n'

    def test_duplicates(self, testlist):
        assert ioh.duplicates(testlist) == [1, 2]

    def test_unique(self, testlist):
        assert ioh.unique(testlist) == [1, 2, 3]

    def test_unique_with_fun(self, testlist):
        def idfun(x):
            return x
        assert ioh.unique(testlist, idfun) == [1, 2, 3]
