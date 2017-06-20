"Test pyhetdex.tools.io_helpers"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import inspect
import sys

import pytest
import six

import pyhetdex.tools.io_helpers as ioh

parametrize = pytest.mark.parametrize


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


@parametrize('answer, is_yes, n_answers',
             [('n', False, 1), ('', False, 1), ('y', True, 1),
              (['n', 'y'], False, 1), (['y', ''], True, 1),
              (['wrong', 'y'], True, 2), (['wrong', 'n'], False, 2),
              (['wrong', ''], False, 2),
              ])
def test_ask_yes_no(monkeypatch, answer, is_yes, n_answers):
    """Ask whether to overwrite a file"""
    calls = []
    if isinstance(answer, six.string_types):
        answers = [answer, ]
    else:
        answers = answer[:]

    class _Anwser(six.StringIO):
        '''"file object" used to replace sys.stdin for the tests. It registers
        the calls to the parent readline method'''
        def readline(self):
            a = six.StringIO.readline(self)
            calls.append(a)
            return a
    monkeypatch.setattr(sys, 'stdin', _Anwser('\n'.join(answers) + '\n'))

    is_answer_yes = ioh.ask_yes_no('a message')

    assert is_answer_yes == is_yes
    assert len(calls) == n_answers


def test_ask_yes_no_eof(monkeypatch):
    """Hitting ctrl-D is like no"""
    calls = []

    class _Anwser(six.StringIO):
        '''"file object" used to replace sys.stdin for the tests. It registers
        the calls to the parent readline method'''
        def readline(self):
            calls.append('')
            a = six.StringIO.readline(self)
            return a
    monkeypatch.setattr(sys, 'stdin', _Anwser(''))

    is_answer_yes = ioh.ask_yes_no('a message')

    assert not is_answer_yes
    assert len(calls) == 1


@parametrize('in_, out_', [('a', 'a'), (b'a', 'a'), (1, 1)])
def test_encode(in_, out_):
    'test encoding'
    value = ioh.decode(in_)
    assert value == out_


def test_get_resource_file():
    '''Make sure that it can correctly get a file from the package'''
    file_content = ioh.get_resource_file('pyhetdex',  'io_helpers.py')
    io_helpers_source = inspect.getsource(ioh)

    assert file_content == io_helpers_source
