"""Test pyhetdex.tools.configuration"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re

import pytest
import six
from six.moves import configparser as confp

import pyhetdex.tools.configuration as pyhconf
if six.PY2:
    from pyhetdex.tools.configuration import (BasicInterpolation,
                                              ExtendedInterpolation,
                                              SectionProxy)
else:
    from configparser import (BasicInterpolation, ExtendedInterpolation,
                              SectionProxy)

parametrize = pytest.mark.parametrize
xfail_value = pytest.mark.xfail(raises=ValueError,
                                reason='Fail to cast a value')


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
             [True, pytest.mark.xfail(raises=confp.NoOptionError,
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
             [True, pytest.mark.xfail(raises=confp.NoOptionError,
                                      reason='Missing option')(False)])
def test_get_list_of_list_nooption(use_default):
    '''Test that the default is correctly returned'''
    section, option = 'section', 'option'
    c = pyhconf.ConfigParser()
    c.read_dict({section: {option: ''}})

    output = c.get_list_of_list(section, 'other_option',
                                use_default=use_default)

    assert output == [[None, None]]


class TestExtendedInterpolation(object):
    "Test the extended interpolation in the configuration parser"
    INTERPOLATION = ExtendedInterpolation()
    INTERPNAME = "ExtendedInterpolation"
    # configuration defaults
    CONF = {"general": {"dir1": "/path/to"},
            "section": {"subdir": "${general:dir1}/subdir",
                        "dir2": "/path/to/other",
                        "file1": "${subdir}/afile",
                        "file2": "${dir2}/otherfile",
                        },
            }

    @classmethod
    def setup_class(cls):
        cls.exp_subdir = "/path/to/subdir"
        cls.exp_file1 = "/path/to/subdir/afile"
        cls.exp_file2 = "/path/to/other/otherfile"
        cls.exp_subdirraw = "${general:dir1}/subdir"
        cls.exp_fileraw1 = "${subdir}/afile"
        cls.exp_fileraw2 = "${dir2}/otherfile"
        # initialise the parser
        c = pyhconf.ConfigParser(interpolation=cls.INTERPOLATION)
        c.read_dict(cls.CONF)
        cls.c = c
        return cls

    def test_in_section_int(self):
        "Intra-section interpolation"
        file2 = self.c.get("section", "file2")
        assert file2 == self.exp_file2

    def test_cross_section_int(self):
        "Cross-section interpolation"
        subdir = self.c.get("section", "subdir")
        assert subdir == self.exp_subdir

    def test_cross_section_int_rec(self):
        "Cross-section recursive interpolation"
        file1 = self.c.get("section", "file1")
        assert file1 == self.exp_file1

    def test_in_section_int_raw(self):
        "Intra-section interpolation, raw"
        file2 = self.c.get("section", "file2", raw=True)
        assert file2 == self.exp_fileraw2

    def test_cross_section_int_raw(self):
        "Cross-section interpolation, raw"
        subdir = self.c.get("section", "subdir", raw=True)
        assert subdir == self.exp_subdirraw

    def test_cross_section_int_rec_raw(self):
        "Cross-section recursive interpolation, raw"
        file1 = self.c.get("section", "file1", raw=True)
        assert file1 == self.exp_fileraw1


class TestDefInterpolation(TestExtendedInterpolation):
    "Test the interpolation in the configuration parser"

    INTERPOLATION = BasicInterpolation()
    INTERPNAME = "BasicInterpolation"

    # configuration defaults
    @classmethod
    def setup_class(cls):
        super(TestDefInterpolation, cls).setup_class()
        # convert ${} into %()s
        r = re.compile(r"\${(.*)\}")
        sub = r"%(\1)s"
        for opt, val in cls.c.items("section"):
            cls.c.set("section", opt, r.sub(sub, val))
        cls.exp_fileraw1 = r.sub(sub, cls.exp_fileraw1)
        cls.exp_fileraw2 = r.sub(sub, cls.exp_fileraw2)
        cls.exp_subdirraw = r.sub(sub, cls.exp_subdirraw)
        return cls

    @pytest.mark.xfail(raises=confp.InterpolationMissingOptionError,
                       reason='interpolation fails')
    def test_cross_section_int(self):
        "Cross-section interpolation fails"
        super(TestDefInterpolation, self).test_cross_section_int()

    @pytest.mark.xfail(raises=confp.InterpolationMissingOptionError,
                       reason='interpolation fails')
    def test_cross_section_int_rec(self):
        "Cross-section recursive interpolation fails"
        super(TestDefInterpolation, self).test_cross_section_int_rec()


class TestMapping(object):
    "Test the mapping interface to the configuration"

    @classmethod
    def setup_class(cls):
        cls.sections = {'section1': {'key1': 'value1',
                                     'key2': 'value2',
                                     'key3': 'value3'},
                        'section2': {'keyA': 'valueA',
                                     'keyB': 'valueB',
                                     'keyC': 'valueC'},
                        'section3': {'bool': 'on',
                                     'int': '42',
                                     'float': '3.14'},
                        }
        # configuration defaults
        c = pyhconf.ConfigParser()
        c.read_dict(cls.sections)
        cls.c = c
        return cls

    def test_in_section(self):
        """Mapping: test 'in' assertion for sections"""
        assert 'section1' in self.c
        assert 'section2' in self.c

    def test_in_option(self):
        """Mapping: test 'in' assertion for options"""
        assert 'key1' in self.c['section1']

    def test_get_section(self):
        """Mapping: test that the section is correctly given"""
        section = self.c['section1']
        assert isinstance(section, SectionProxy)

    def test_get_option(self):
        """Mapping: test that the option is correctly given"""
        section = self.c['section1']
        assert section['key1'] == 'value1'

    def test_n_options(self):
        """Mapping: test that the number of options is correct"""
        section = self.c['section1']
        assert len(section) == len(self.sections['section1'])

    def test_n_sections(self):
        """Mapping: test that the number of sections is correct"""
        assert len(self.c) == len(self.sections)+1

    @pytest.mark.xfail(raises=KeyError,
                       reason='missing section')
    def test_no_section(self):
        """Mapping: ask for the wrong section"""
        self.c['nosection']

    @pytest.mark.xfail(raises=KeyError,
                       reason='missing option')
    def test_no_option(self):
        """Mapping: ask for the wrong option"""
        try:
            section = self.c['section2']
        except KeyError:
            raise confp.NoSectionError('section2')
        section['key']

    def test_add_rm_section(self):
        """Mapping: add and remove a new section"""
        self.c['new_section'] = {}
        assert self.c.has_section('new_section')
        assert len(self.c) == len(self.sections)+2
        del self.c['new_section']
        assert not self.c.has_section('new_section')

    def test_add_rm_option(self):
        """Mapping: add and remove a new option"""
        self.c['section1']['key4'] = 'value4'
        assert self.c.has_option('section1', 'key4')
        assert self.c.get('section1', 'key4') == 'value4'
        del self.c['section1']['key4']
        assert not self.c.has_option('section1', 'key4')

    @pytest.mark.xfail(raises=KeyError,
                       reason='trying to delete missing section')
    def test_delete_wrong_section(self):
        """Mapping: delete a non existing section"""
        del self.c['no_exists']

    @pytest.mark.xfail(raises=KeyError,
                       reason='trying to delete missing option')
    def test_delete_wrong_option(self):
        """Mapping: delete a non existing option"""
        try:
            section = self.c['section2']
        except KeyError:
            raise confp.NoSectionError('section2')
        del section['no_exists']

    def test_get_option_get(self):
        """Get options value with get"""
        section = self.c['section1']
        assert section.get('key1') == self.c['section1']['key1']

    def test_get_no_option_fallback(self):
        """Get options value with get and"""
        section = self.c['section1']
        assert section.get('key') is None

    def test_get_no_option_custom_fallback(self):
        """Get options value with get and"""
        section = self.c['section1']
        assert section.get('key', 'a value') == 'a value'

    def test_getboolean(self):
        section = self.c['section3']
        assert section.getboolean('bool')

    def test_getboolean_fallback(self):
        section = self.c['section3']
        assert not section.getboolean('boo', False)

    def test_getint(self):
        section = self.c['section3']
        assert section.getint('int') == 42

    def test_getint_fallback(self):
        section = self.c['section3']
        assert section.getint('in', 43) == 43

    def test_getfloat(self):
        section = self.c['section3']
        assert section.getfloat('float') == 3.14

    def test_getfloat_fallback(self):
        section = self.c['section3']
        assert section.getfloat('floa', 2.71) == 2.71
