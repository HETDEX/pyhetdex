"""Test pyhetdex.tools.configuration"""

import re

import nose.tools as nt
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


class TestConf(object):
    "Test the configuration"

    @classmethod
    def setup_class(cls):
        # configuration defaults
        conf = {"listolist": {"lists": "3500-4500,4500-5500"},
                "list": {"float_list": "3500, 4500, 5500",
                         "literal_list": "['a', 'b', 'c']",
                         "literal_list2": "a, b, c",
                         },
                "empty": {"empty_list": " ",
                          "literal_empty_list": "[]",
                          },
                "one": {'list': "3500",
                        'listolist': "3500-4500", },
                }
        cls.lists_exp = [[3500, 4500], [4500, 5500]]
        cls.float_list_exp = [3500, 4500, 5500]
        cls.literal_list_exp = ['a', 'b', 'c']
        cls.empty_list_exp = []
        cls.empty_list_of_list_exp = [[None, None]]
        # initialise the parser
        c = pyhconf.ConfigParser()
        c.read_dict(conf)
        cls.c = c
        return cls

    def test_empty_list(self):
        "empty list"
        emptyl = self.c.get_list('empty', 'empty_list')
        nt.assert_equal(emptyl, self.empty_list_exp)

    def test_literal_empty_list(self):
        "literal empty list"
        emptyl = self.c.get_list('empty', 'literal_empty_list')
        nt.assert_equal(emptyl, self.empty_list_exp)

    def test_empty_list_of_list(self):
        "empty list of lists"
        emptyl = self.c.get_list_of_list('empty', 'empty_list')
        nt.assert_equal(emptyl, self.empty_list_of_list_exp)

    def test_list_of_list(self):
        "list of lists"
        lols = self.c.get_list_of_list('listolist', 'lists')
        nt.assert_equal(lols, self.lists_exp)

    def test_list_of_list_def(self):
        "list of lists, use default"
        lols = self.c.get_list_of_list('listolist', 'noexist',
                                       use_default=True)
        nt.assert_equal(lols, [[None, None]])

    @nt.raises(confp.NoOptionError)
    def test_list_of_list_fail(self):
        "list of lists, use default"
        self.c.get_list_of_list('listolist', 'noexist')

    def test_list_float(self):
        "list of numbers"
        l = self.c.get_list('list', 'float_list')
        nt.assert_equal(l, self.float_list_exp)

    def test_list_literals(self):
        "list of literals"
        l = self.c.get_list('list', 'literal_list')
        nt.assert_equal(l, self.literal_list_exp)

    def test_list_literals2(self):
        "list of literals, as comma separated values"
        l = self.c.get_list('list', 'literal_list2')
        nt.assert_equal(l, self.literal_list_exp)

    def test_list_def(self):
        "list of numbers, use default"
        l = self.c.get_list('list', 'noexist', use_default=True)
        nt.assert_equal(l, [])

    @nt.raises(confp.NoOptionError)
    def test_list_fail(self):
        "list of lists, use default"
        self.c.get_list('list', 'noexist')

    def test_list_one_element(self):
        """List of one element, without commas"""
        l = self.c.get_list('one', 'list')
        nt.assert_equal(l, [3500])

    def test_listolist_one_element(self):
        """List of lists of one element, without commas"""
        l = self.c.get_list_of_list('one', 'listolist')
        nt.assert_equal(l, [[3500, 4500]])


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
        nt.assert_equal(file2, self.exp_file2)

    def test_cross_section_int(self):
        "Cross-section interpolation"
        subdir = self.c.get("section", "subdir")
        nt.assert_equal(subdir, self.exp_subdir)

    def test_cross_section_int_rec(self):
        "Cross-section recursive interpolation"
        file1 = self.c.get("section", "file1")
        nt.assert_equal(file1, self.exp_file1)

    def test_in_section_int_raw(self):
        "Intra-section interpolation, raw"
        file2 = self.c.get("section", "file2", raw=True)
        nt.assert_equal(file2, self.exp_fileraw2)

    def test_cross_section_int_raw(self):
        "Cross-section interpolation, raw"
        subdir = self.c.get("section", "subdir", raw=True)
        nt.assert_equal(subdir, self.exp_subdirraw)

    def test_cross_section_int_rec_raw(self):
        "Cross-section recursive interpolation, raw"
        file1 = self.c.get("section", "file1", raw=True)
        nt.assert_equal(file1, self.exp_fileraw1)


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

    @nt.raises(confp.InterpolationMissingOptionError)
    def test_cross_section_int(self):
        "Cross-section interpolation fails"
        super(TestDefInterpolation, self).test_cross_section_int()

    @nt.raises(confp.InterpolationMissingOptionError)
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
                        }
        # configuration defaults
        c = pyhconf.ConfigParser()
        c.read_dict(cls.sections)
        cls.c = c
        return cls

    def test_in_section(self):
        """Mapping: test 'in' assertion for sections"""
        nt.assert_in('section1', self.c)
        nt.assert_in('section2', self.c)

    def test_in_option(self):
        """Mapping: test 'in' assertion for options"""
        nt.assert_in('key1', self.c['section1'])

    def test_get_section(self):
        """Mapping: test that the section is correctly given"""
        section = self.c['section1']
        nt.assert_is_instance(section, SectionProxy)

    def test_get_option(self):
        """Mapping: test that the option is correctly given"""
        section = self.c['section1']
        nt.assert_equal(section['key1'], 'value1')

    def test_n_options(self):
        """Mapping: test that the number of options is correct"""
        section = self.c['section1']
        nt.assert_equal(len(section), len(self.sections['section1']))

    def test_n_sections(self):
        """Mapping: test that the number of sections is correct"""
        nt.assert_equal(len(self.c), len(self.sections)+1)

    @nt.raises(KeyError)
    def test_no_section(self):
        """Mapping: ask for the wrong section"""
        self.c['section3']

    @nt.raises(KeyError)
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
        nt.assert_true(self.c.has_section('new_section'))
        nt.assert_equal(len(self.c), len(self.sections)+2)
        del self.c['new_section']
        nt.assert_false(self.c.has_section('new_section'))

    def test_add_rm_option(self):
        """Mapping: add and remove a new option"""
        self.c['section1']['key4'] = 'value4'
        nt.assert_true(self.c.has_option('section1', 'key4'))
        nt.assert_equal(self.c.get('section1', 'key4'), 'value4')
        del self.c['section1']['key4']
        nt.assert_false(self.c.has_option('section1', 'key4'))

    @nt.raises(KeyError)
    def test_delete_wrong_section(self):
        """Mapping: delete a non existing section"""
        del self.c['no_exists']

    @nt.raises(KeyError)
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
        nt.assert_equal(section.get('key1'), self.c['section1']['key1'])

    def test_get_no_option_fallback(self):
        """Get options value with get and"""
        section = self.c['section1']
        nt.assert_equal(section.get('key'), None)

    def test_get_no_option_custom_fallback(self):
        """Get options value with get and"""
        section = self.c['section1']
        nt.assert_equal(section.get('key', 'a value'), 'a value')
