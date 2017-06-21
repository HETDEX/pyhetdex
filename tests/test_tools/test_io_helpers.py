"Test pyhetdex.tools.io_helpers"
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import inspect
import os
import sys

import pytest
import six

import pyhetdex.tools.io_helpers as ioh

parametrize = pytest.mark.parametrize


@pytest.fixture
def testfile():
    '''Return a StringIO to mock a file object'''
    s = six.StringIO('# Comment\n#!\n#\n\nTest <123>\n[ 1 2 3 ]\n')
    return s


@pytest.fixture
def testlist():
    'return a list of integers'
    return [1, 1, 1, 2, 1, 3, 2, 1]


def test_countlines(testfile):
    assert ioh.count_lines(testfile) == 6


def test_eat_to_char(testfile):
    assert ioh.eat_to_char(testfile, '<') == '<'


def test_eat_to_blockstart(testfile):
    assert ioh.eat_to_blockstart(testfile) == ' '


def test_read_to_char(testfile):
    assert ioh.read_to_char(testfile, '!') == '# Comment #'


def test_read_to_char_noskipnewline(testfile):
    assert ioh.read_to_char(testfile, '!', False) == '# Comment\n#'


@parametrize('lines, first_line',
             [('#Comment\nTest <123>\n', 'Test <123>\n'),
              ('#Comment\n\nTest <123>\nother\n', 'Test <123>\n'),
              ('Test <123>\nother\n', 'Test <123>\n'),
              ('#Comment\n', ''), ('', '')])
def test_skip_comment(lines, first_line):
    line = ioh.skip_commentlines(six.StringIO(lines))
    assert line == first_line


def test_duplicates(testlist):
    assert ioh.duplicates(testlist) == [1, 2]


def test_unique(testlist):
    assert ioh.unique(testlist) == [1, 2, 3]


def test_unique_with_fun(testlist):
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
    file_content = ioh.get_resource_file('pyhetdex',
                                         os.path.join('tools',
                                                      'io_helpers.py'))
    io_helpers_source = inspect.getsource(ioh)

    assert file_content == io_helpers_source


@parametrize('verbose', [True, False])
def test_copy_resources(tmpdir, capsys, verbose):
    '''Copy the files to destination'''
    files = [os.path.join('tools', 'io_helpers.py'), '__init__.py']

    written, non_written, backup = ioh.copy_resources('pyhetdex', files,
                                                      tmpdir.strpath,
                                                      verbose=verbose)

    assert written == files
    assert not non_written
    assert not backup

    out = [i.relto(tmpdir) for i in tmpdir.visit() if i.check(dir=False)]
    assert sorted(out) == sorted(files)

    stdout, stderr = capsys.readouterr()
    assert (len(stdout) > 0) == verbose
    assert not stderr


@parametrize('backup', [True, False])
@parametrize('overwrite', [True, False])
@parametrize('is_yes', [True, False])
def test_copy_resources_overwrite(tmpdir, monkeypatch, backup, overwrite,
                                  is_yes):
    '''Copy the files to destination adding options'''
    files = [os.path.join('tools', 'io_helpers.py'), '__init__.py']
    tmpdir.ensure('__init__.py')

    monkeypatch.setattr(ioh, 'ask_yes_no', lambda _: is_yes)

    has_backup = backup and (not overwrite)

    written, non_written, backedup = ioh.copy_resources('pyhetdex', files,
                                                        tmpdir.strpath,
                                                        backup=backup,
                                                        force=overwrite)

    assert (written == files) == (backup or overwrite or is_yes)
    assert (len(non_written) == 0) == (backup or overwrite or is_yes)
    assert (len(backedup) == 1) == has_backup

    out = [i.relto(tmpdir) for i in tmpdir.visit() if i.check(dir=False)]
    expected = 3 if has_backup else 2
    assert len(out) == expected


def test_copy_resources_replace(tmpdir):
    '''Copy the files to destination modifying the file'''
    files = [os.path.join('tools', 'io_helpers.py'), '__init__.py']

    def replace(fcontent):
        '''replace NameError with __42__'''
        return fcontent.replace('NameError', '__42__')

    written, non_written, backedup = ioh.copy_resources('pyhetdex', files,
                                                        tmpdir.strpath,
                                                        replace_func=replace)

    init = tmpdir.join('__init__.py').read()
    assert '__42__' not in init

    io_helper = tmpdir.join('tools', 'io_helpers.py').read()
    assert '__42__' in io_helper
    assert 'NameError' not in io_helper


@parametrize('header, list_, printed',
             [('test', [], False), ('test', ['a', ] * 100, True),
              ('\x1b[31mtest\x1b[39m', ['a', ] * 100, True)])
def test_print_list(capsys, header, list_, printed):
    '''Print the list as necessary'''
    has_printed = ioh.print_list(header, list_)

    assert has_printed == printed

    stdout, _ = capsys.readouterr()
    assert ('test' in stdout) == printed

    if printed:
        lines = stdout.splitlines()

        for l in lines[1:]:
            assert l.startswith('    a')
