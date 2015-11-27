"Test pyhetdex.tools.io_helpers"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pyhetdex.tools.io_helpers as ioh
import pytest


@pytest.fixture()
def testfile(request, tmpdir):
    fname = tmpdir.mkdir('io').join('test.txt')
    fout = fname.open('w')
    fout.write('# Comment\n')
    fout.write('#!\n')
    fout.write('#\n')
    fout.write('\n')
    fout.write('Test <123>\n')
    fout.write('[ 1 2 3 ]\n')
    fout.close()

    fin = fname.open()

    def final():
        fin.close()
    request.addfinalizer(final)

    return fin


@pytest.fixture(scope='module')
def testlist():
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

    def test_duplicates(self, testlist):
        assert ioh.duplicates(testlist) == [1, 2]

    def test_unique(self, testlist):
        assert ioh.unique(testlist) == [1, 2, 3]

    def test_unique_with_fun(self, testlist):
        def idfun(x):
            return x
        assert ioh.unique(testlist, idfun) == [1, 2, 3]
