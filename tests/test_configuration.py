"""Test pyhetdex.tools.configuration"""

import re
try:  # python 2.x
    import ConfigParser as confp
    from pyhetdex.tools.configuration import (BasicInterpolation,
                                              ExtendedInterpolation)
except ImportError:  # python 3.x
    import configparser as confp
    from configparser import BasicInterpolation, ExtendedInterpolation

import nose.tools as nt

import pyhetdex.tools.configuration as pyhconf


class TestConf(object):
    "Test the configuration"

    @classmethod
    def setup_class(cls):
        # configuration defaults
        conf = {"listolist": {"lists": "3500-4500,4500-5500"},
                "list": {"float_list": "3500, 4500, 5500",
                         "literal_list": "['a', 'b', 'c']",
                         "literal_list2": "a, b, c"
                         },
                }
        cls.lists_exp = [[3500, 4500], [4500, 5500]]
        cls.float_list_exp = [3500, 4500, 5500]
        cls.literal_list_exp = ['a', 'b', 'c']
        # initialise the parser
        c = pyhconf.ConfigParser()
        c.read_dict(conf)
        cls.c = c
        return cls

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
