"""Test pyhetdex.tools.configuration"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from argparse import Namespace

import pytest
import configparser

import pyhetdex.tools.configuration as pyhconf

parametrize = pytest.mark.parametrize
xfail_value = pytest.mark.xfail(raises=ValueError,
                                reason='Fail to cast a value')


@parametrize('attr, val, modified, expected',
             [('other', 'test', False, ''),
              ('setting__sec2', 'test', False, ''),
              ('setting__sec1__opt1', None, False, ''),
              ('setting__sec1__opt1', [], False, ''),
              ('setting__sec1__opt1', 'test', True, 'test'),
              ('setting__sec1__opt1', 42, True, '42'),
              ('setting__sec1__opt1', [42, 43], True, '42, 43'),
              ('setting__sec1__opt2', 'test', False, ''),
              ('setting__sec2__opt1', 'test', False, ''),
              ])
def test_override_conf(attr, val, modified, expected):
    '''Configuration override'''
    c = pyhconf.ConfigParser()
    c.read_dict({'sec1': {'opt1': 'val1'}})

    args = Namespace(**{attr: val})

    c = pyhconf.override_conf(c, args)

    assert len(c) == 2
    assert len(c['sec1']) == 1

    new_val = c['sec1']['opt1']
    assert (new_val == 'val1') != modified
    if modified:
        assert new_val == expected


@parametrize('value, cast_to, recovered',
             [('', str, []), ('', int, []),
              ('a, b , c  ', str, ['a', 'b', 'c']),
              xfail_value(('a, b , c  ', int, ['a', 'b', 'c'])),
              ('1, 2 , 3  ', int, [1, 2, 3]),
              ('1, 2 , 3  ', float, [1., 2., 3.]),
              ('1, yes, true, on', bool, [True, ] * 4),
              ('0, no, false, off', bool, [False, ] * 4),
              xfail_value(('nobool, no, ', bool, [False, ] * 2)),
              ])
def test_get_list(value, cast_to, recovered):
    '''Test getting lists from the configuration'''
    section, option = 'section', 'option'
    c = pyhconf.ConfigParser()
    c.read_dict({section: {option: value}})

    output = c.get_list(section, option, cast_to=cast_to)

    assert output == recovered


@parametrize('use_default',
             [True, pytest.mark.xfail(raises=configparser.NoOptionError,
                                      reason='Missing option')(False)])
def test_get_list_nooption(use_default):
    '''Test that the default is correctly returned'''
    section, option = 'section', 'option'
    c = pyhconf.ConfigParser()
    c.read_dict({section: {option: ''}})

    output = c.get_list(section, 'other_option', use_default=use_default)

    assert output == []


@parametrize('value, cast_to, recovered',
             [('', str, [[None, None]]), ('', int, [[None, None]]),
              ('a-b , c-d  ', str, [['a', 'b'], ['c', 'd']]),
              xfail_value(('a-b , c-d  ', int, [])),
              ('1 - 2 , 3 -4 ', int, [[1, 2], [3, 4]]),
              ('1 - 2 , 3 -4 ', float, [[1., 2.], [3., 4.]]),
              ('1- yes, true- on', bool, [[True, True], ] * 2),
              ('0- no, false- off', bool, [[False, False], ] * 2),
              xfail_value(('nobool, no, ', bool, [])),
              ])
def test_get_list_of_list(value, cast_to, recovered):
    '''Test getting lists from the configuration'''
    section, option = 'section', 'option'
    c = pyhconf.ConfigParser()
    c.read_dict({section: {option: value}})

    output = c.get_list_of_list(section, option, cast_to=cast_to)

    assert output == recovered


@parametrize('use_default',
             [True, pytest.mark.xfail(raises=configparser.NoOptionError,
                                      reason='Missing option')(False)])
def test_get_list_of_list_nooption(use_default):
    '''Test that the default is correctly returned'''
    section, option = 'section', 'option'
    c = pyhconf.ConfigParser()
    c.read_dict({section: {option: ''}})

    output = c.get_list_of_list(section, 'other_option',
                                use_default=use_default)

    assert output == [[None, None]]


def test_interpolation_warning():
    '''Make sure that the six.moves addition are deprecated'''
    from six.moves import BasicInterpolation, ExtendedInterpolation

    with pytest.warns(DeprecationWarning):
        BasicInterpolation()

    with pytest.warns(DeprecationWarning):
        ExtendedInterpolation()


def test_read_file(tmpdir):
    '''Make sure that ``ConfigParser.read_file`` is available in python 2'''
    conf_file = tmpdir.join('tmp.cfg')
    conf_file.write('[general]\noption = value\n')

    c = pyhconf.ConfigParser()
    c.read_file(conf_file.open())

    assert 'general' in c
    assert c['general']['option'] == 'value'
