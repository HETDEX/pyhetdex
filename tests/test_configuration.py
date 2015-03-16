"""Test pyhetdex.tools.configuration"""

try:  # python 2.x
    import ConfigParser as confp
except ImportError:  # python 3.x
    import configparser as confp

import nose.tools as nt

import pyhetdex.tools.configuration as pyhconf

# configuration dictionary
conf = {"listolist": {"lists": "3500-4500,4500-5500"},
        "list": {"float_list": "3500, 4500, 5500",
                 "literal_list": "['a', 'b', 'c']",
                 "literal_list2": "a, b, c"
                 },
        }
lists_exp = [[3500, 4500], [4500, 5500]]
float_list_exp = [3500, 4500, 5500]
literal_list_exp = ['a', 'b', 'c']


class TestConf(object):
    "Test the configuration"

    @classmethod
    def setup_class(cls):
        c = pyhconf.ConfigParser()
        c.read_dict(conf)
        cls.c = c
        return cls

    def test_list_of_list(self):
        "list of lists"
        lols = self.c.get_list_of_list('listolist', 'lists')
        nt.assert_equal(lols, lists_exp)

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
        nt.assert_equal(l, float_list_exp)

    def test_list_literals(self):
        "list of literals"
        l = self.c.get_list('list', 'literal_list')
        nt.assert_equal(l, literal_list_exp)

    def test_list_literals2(self):
        "list of literals, as comma separated values"
        l = self.c.get_list('list', 'literal_list2')
        nt.assert_equal(l, literal_list_exp)

    def test_list_def(self):
        "list of numbers, use default"
        l = self.c.get_list('list', 'noexist', use_default=True)
        nt.assert_equal(l, [])

    @nt.raises(confp.NoOptionError)
    def test_list_fail(self):
        "list of lists, use default"
        self.c.get_list('list', 'noexist')

    def test_read_dict(self):
        "failures in reading a dictionary"
        self.c.read_dict({"list": {"float_list": "element"},
                          })
