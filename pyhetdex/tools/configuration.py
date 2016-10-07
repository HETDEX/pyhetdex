"""Configuration set up

The custom :class:`ConfigParser` provides two new functionalities to parse
lists:

* :meth:`ConfigParser.get_list`
* :meth:`ConfigParser.get_list_of_list`

Also it extends the python 2.x configuration parser with features coming from
python 3:

* :meth:`ConfigParser.read_dict`
* the possibility to use `extended interpolation
  <https://docs.python.org/3.4/library/configparser.html#configparser.ExtendedInterpolation>`_
* mapping protocol as described `here
  <https://docs.python.org/3.5/library/configparser.html#mapping-protocol-access>`_.

Examples
--------
>>> import pyhetdex.tools.configuration as pconf
>>> # This can be imported only after `pyhetdex.tools.configuration` has been
>>> # imported
>>> from six.moves import BasicInterpolation
>>> from six.moves import ExtendedInterpolation
>>> # standard config parser interpolation
>>> stdparser = pconf.ConfigParser()
>>> # equivalent
>>> stdparser = pconf.ConfigParser(interpolation=BasicInterpolation())
>>> # extended config parser interpolation
>>> extparser = pconf.ConfigParser(interpolation=ExtendedInterpolation())
>>> # test mapping interface
>>> parser = ConfigParser()
>>> sections = {'section1': {'key1': 'value1',
...                          'key2': 'value2',
...                          'key3': 'value3'},
...             'section2': {'keyA': 'valueA',
...                          'keyB': 'valueB',
...                          'keyC': 'valueC'},
...             }
>>> parser.read_dict(sections)
>>> parser['section1']
<Section: section1>
>>> print(parser['section2']['keyA'])
valueA

::

    # Configuration file: default interpolation
    [general]
    dir1 = /path/to
    [section]
    dir1 = /path/to
    file1 = %(dir1)/file1

    # Configuration file: extended interpolation
    [general]
    dir1 = /path/to
    [section]
    file1 = %{general:dir1}/file1
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import itertools
import re

import six
import six.moves.configparser as confp


# =============================================================================
# Custom configuration parser. Provides extra get methods to parse and store
# complex options
# =============================================================================
class ConfigParser(confp.ConfigParser):
    """Customise configuration parser

    For pyhton 3 all the ``args`` and ``kwargs`` are passed to the constructor
    of the parent class. For python 2 the extra keyword ``interpolation`` is
    added.

    Parameters
    ----------
    args : list
        arguments passed to the parent class
    kwargs : dict
        keyword arguments passed to the parent class
    interpolation : :class:`Interpolation` instance
        only for python 2: select which interpolation to use
    """
    def __init__(self, *args, **kwargs):
        try:  # python 3
            super(ConfigParser, self).__init__(*args, **kwargs)
        except TypeError:  # python 2: ConfigParser is old style
            # get the interpolation and default to the BasicInterpolation:
            # should work as the standard python 2 one
            self._interpolation = kwargs.pop('interpolation',
                                             BasicInterpolation())
            confp.ConfigParser.__init__(self, *args, **kwargs)
            self.default_section = confp.DEFAULTSECT

        try:  # Python 2
            self.BOOLEAN_STATES = self._boolean_states
        except AttributeError:  # better pythons
            self.BOOLEAN_STATES = self.BOOLEAN_STATES

    def _to_boolean(self, value):
        '''Convert a string to a boolean compatible to ConfigParser standards

        Parameters
        ----------
        value : string
            input value

        Returns
        -------
        bool
            converted value

        Raises
        ------
        ValueError
            if the conversion fails
        '''
        try:
            return self.BOOLEAN_STATES[value.lower()]
        except KeyError:
            raise ValueError('Not a boolean: %s' % value)

    def get_list_of_list(self, section, option, use_default=False):
        """
        A convenience method which coerces the option in the specified section
        to a list of lists. If the options is empty returns ``[[None, None]]``

        Examples
        --------
        .. testsetup:: *

            from pyhetdex.tools.configuration import ConfigParser

        >>> # cat settings.cfg:
        >>> # [section]
        >>> # wranges_bkg = 3500-4500,4500-5500
        >>> conf = ConfigParser()
        >>> conf.read_dict({"section": {"wranges_bkg": "3500-4500,4500-5500"}})
        >>> conf.get_list_of_list("section", "wranges_bkg")
        [[3500.0, 4500.0], [4500.0, 5500.0]]
        >>> conf.get_list_of_list("section", "not_exist")
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        NoOptionError: No option 'not_exist' in section: 'section'
        >>> conf.get_list_of_list("section", "not_exist", use_default=True)
        [[None, None]]

        Parameters
        ----------

        section : string
            name of the section
        option : string
            name of the option
        use_default : bool
            whether default to ``[[None, None]]``

        Returns
        -------
        value : list of lists
            parsed option

        Raises
        ------
        NoOptionError
            if the option doesn't exist and no default required
        """
        try:
            value = self.get(section, option)
        except confp.NoOptionError:
            if use_default:
                return [[None, None]]
            else:
                raise

        if not value.strip():
            return [[None, None]]

        value = value.split(',')  # divide the various groups
        # split each of the '-' separated couples and convert to float
        value = [list(map(float, i.split('-'))) for i in value]
        return value

    def get_list(self, section, option, use_default=False, cast_to=str):
        """A convenience method which converts the option in the specified section
        from a comma separated list to a python list.

        If the options is empty returns the empty list ``[]``.

        Examples
        --------

        .. testsetup:: *

            from pyhetdex.tools.configuration import ConfigParser

        >>> # cat settings.cfg:
        >>> # [section]
        >>> # wranges_iq = 3500, 4500, 5500
        >>> conf = ConfigParser()
        >>> conf.read_dict({"section": {"wranges_iq": "3500, 4500, 5500"}})
        >>> conf.get_list("section", "wranges_iq")
        ['3500', '4500', '5500']
        >>> conf.get_list("section", "wranges_iq", cast_to=int)
        [3500, 4500, 5500]
        >>> conf.get_list("section", "not_exist")
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        NoOptionError: No option 'not_exist' in section: 'section'
        >>> conf.get_list("section", "not_exist", use_default=True)
        []

        Parameters
        ----------
        section : string
            name of the section
        option : string
            name of the option
        use_default : bool, optional
            whether default to ``[]``
        cast_to : type, optional
            convert each element to the given type; default convert to string.
            The ``bool`` case is treated especially to comply with the
            ConfigParser standards.

        Returns
        -------
        value : list of lists
            parsed option

        Raises
        ------
        NoOptionError
            if the option doesn't exist and no default required
        """
        try:
            value = self.get(section, option)
        except confp.NoOptionError:
            if use_default:
                return []
            else:
                raise

        if not value.strip():
            value = []
        else:
            if cast_to == bool:
                cast_to = self._to_boolean
            value = [cast_to(v.strip()) for v in value.split(',')]

        return value

    def read_dict(self, dictionary, source='<dict>'):
        """Read configuration from a dictionary.

        Keys are section names, values are dictionaries with keys and values
        that should be present in the section. If the used dictionary type
        preserves order, sections and their keys will be added in order.

        All types held in the dictionary are converted to strings during
        reading, including section names, option names and keys.

        Optional second argument is the ``source`` specifying the name of the
        dictionary being read.

        Notes
        -----
        This method provides an implementation (taken from python3.4
        configparser module) if the method is not already present in
        :class:`~confp.ConfigParser` (thus for python <3.2)
        """
        try:  # python >= 3.2
            super(ConfigParser, self).read_dict(dictionary, source=source)
        except (AttributeError, TypeError):  # otherwise
            elements_added = set()
            for section, keys in dictionary.items():
                section = str(section)
                try:
                    self.add_section(section)
                except (confp.DuplicateSectionError, ValueError):
                    if section in elements_added:
                        raise
                elements_added.add(section)
                for key, value in keys.items():
                    key = self.optionxform(str(key))
                    if value is not None:
                        value = str(value)
                    if (section, key) in elements_added:
                        raise confp.DuplicateOptionError(section, key, source)
                    elements_added.add((section, key))
                    self.set(section, key, value)

    def _interpolate(self, section, option, rawval, vars):
        """In python 2 replaces the standard interpolation with an instance
        derived from :class:`Interpolation`. This method is never called by
        python 3
        """
        return self._interpolation.before_get(self, section, option, rawval,
                                              vars)

    def __getitem__(self, key):
        try:
            return super(ConfigParser, self).__getitem__(key)
        except TypeError:
            # python 2: ConfigParser is old style and doesn't have mapping
            # style access
            if key != self.default_section and not self.has_section(key):
                raise KeyError(key)
            return SectionProxy(self, key)

    def __setitem__(self, key, value):
        try:
            super(ConfigParser, self).__setitem__(key, value)
        except TypeError:
            # To conform with the mapping protocol, overwrites existing values
            # in the section.
            self.remove_section(key)
            self.read_dict({key: value})

    def __delitem__(self, key):
        try:
            super(ConfigParser, self).__delitem__(key)
        except TypeError:
            if key == self.default_section:
                raise ValueError("Cannot remove the default section.")
            if not self.has_section(key):
                raise KeyError(key)
            self.remove_section(key)

    def __contains__(self, key):
        try:
            return super(ConfigParser, self).__contains__(key)
        except TypeError:
            return key == self.default_section or self.has_section(key)

    def __len__(self):
        try:
            return super(ConfigParser, self).__len__()
        except TypeError:
            return len(self._sections) + 1  # the default section

    def __iter__(self):
        try:
            return super(ConfigParser, self).__iter__()
        except TypeError:
            # XXX does it break when underlying container state changed?
            return itertools.chain((self.default_section,),
                                   self._sections.keys())


class SectionProxy():
    """A proxy for a single section from a parser.

    Adapted for the use with python 2.7 from `the python 3.4 implementation
    <https://hg.python.org/cpython/file/3.4/Lib/configparser.py#l1189>`_
    """

    def __init__(self, parser, name):
        """Creates a view on a section of the specified `name` in `parser`."""
        self._parser = parser
        self._name = name

    def __repr__(self):
        return '<Section: {}>'.format(self._name)

    def __getitem__(self, key):
        if not self._parser.has_option(self._name, key):
            raise KeyError(key)
        return self._parser.get(self._name, key)

    def __setitem__(self, key, value):
        return self._parser.set(self._name, key, value)

    def __delitem__(self, key):
        if not (self._parser.has_option(self._name, key) and
                self._parser.remove_option(self._name, key)):
            raise KeyError(key)

    def __contains__(self, key):
        return self._parser.has_option(self._name, key)

    def __len__(self):
        return len(self._options())

    def __iter__(self):
        return self._options().__iter__()

    def _options(self):
        if self._name != self._parser.default_section:
            return self._parser.options(self._name)
        else:
            return self._parser.defaults()

    @property
    def parser(self):
        # The parser object of the proxy is read-only.
        return self._parser

    @property
    def name(self):
        # The name of the section on a proxy is read-only.
        return self._name

    def _get(self, method, option, fallback=None, **kwargs):
        """Use the ``method`` to get the option"""
        try:
            return method(self._name, option, **kwargs)
        except confp.NoOptionError:
            return fallback

    def get(self, option, fallback=None, raw=False, vars=None):
        """Get an option value."""
        return self._get(self._parser.get, option, fallback=fallback, raw=raw,
                         vars=vars)

    def getboolean(self, option, fallback=None, raw=False, vars=None):
        """Get an option value as a boolean."""
        return self._get(self._parser.getboolean, option, fallback=fallback)

    def getint(self, option, fallback=None, raw=False, vars=None):
        """Get an option value as a boolean."""
        return self._get(self._parser.getint, option, fallback=fallback)

    def getfloat(self, option, fallback=None, raw=False, vars=None):
        """Get an option value as a boolean."""
        return self._get(self._parser.getfloat, option, fallback=fallback)


# =============================================================================
# Copied from python 3.5.dev to enable cross-section interpolation in python
# 2.7
# =============================================================================
class Interpolation(object):
    """Dummy interpolation that passes the value through with no
    changes."""

    def before_get(self, parser, section, option, value, defaults):
        return value

    def before_set(self, parser, section, option, value):
        return value

    def before_read(self, parser, section, option, value):
        return value

    def before_write(self, parser, section, option, value):
        return value


class BasicInterpolation(Interpolation):
    """Interpolation as implemented in the classic python 3 ConfigParser.

    The option values can contain format strings which refer to other
    values in the same section, or values in the special default section.

    For example::

        something: %(dir)s/whatever

    would resolve the ``%(dir)s`` to the value of dir.  All reference
    expansions are done late, on demand. If a user needs to use a bare ``%`` in
    a configuration file, she can escape it by writing ``%%``. Other ``%``
    usage is considered a user error and raises
    :class:`~configparser.InterpolationSyntaxError`.
    """

    _KEYCRE = re.compile(r"%\(([^)]+)\)s")

    def before_get(self, parser, section, option, value, defaults):
        L = []
        self._interpolate_some(parser, option, L, value, section, defaults,
                               1)
        return ''.join(L)

    def before_set(self, parser, section, option, value):
        tmp_value = value.replace('%%', '')  # escaped percent signs
        tmp_value = self._KEYCRE.sub('', tmp_value)  # valid syntax
        if '%' in tmp_value:
            raise ValueError("invalid interpolation syntax in %r at "
                             "position %d" % (value, tmp_value.find('%')))
        return value

    def _interpolate_some(self, parser, option, accum, rest, section, map,
                          depth):
        if depth > confp.MAX_INTERPOLATION_DEPTH:
            raise confp.InterpolationDepthError(option, section, rest)
        while rest:
            p = rest.find("%")
            if p < 0:
                accum.append(rest)
                return
            if p > 0:
                accum.append(rest[:p])
                rest = rest[p:]
            # p is no longer used
            c = rest[1:2]
            if c == "%":
                accum.append("%")
                rest = rest[2:]
            elif c == "(":
                m = self._KEYCRE.match(rest)
                if m is None:
                    msg = ("bad interpolation variable reference"
                           " {}".format(rest))
                    raise confp.InterpolationSyntaxError(option, section, msg)
                var = parser.optionxform(m.group(1))
                rest = rest[m.end():]
                try:
                    v = map[var]
                except KeyError:
                    raise confp.InterpolationMissingOptionError(
                        option, section, rest, var)
                if "%" in v:
                    self._interpolate_some(parser, option, accum, v,
                                           section, map, depth + 1)
                else:
                    accum.append(v)
            else:
                raise confp.InterpolationSyntaxError(
                    option, section,
                    "'%%' must be followed by '%%' or '(', "
                    "found: %r" % (rest,))


class ExtendedInterpolation(Interpolation):
    """Advanced variant of interpolation, supports the syntax used by
    ``zc.buildout``. Enables interpolation between sections.

    For example::

        [general]
        dir1 = /path/to
        [section]
        file1 = %{general:dir1}/file1


    would resolve ``file1 = /path/to/file1``.
    """

    _KEYCRE = re.compile(r"\$\{([^}]+)\}")

    def before_get(self, parser, section, option, value, defaults):
        L = []
        self._interpolate_some(parser, option, L, value, section, defaults,
                               1)
        return ''.join(L)

    def before_set(self, parser, section, option, value):
        tmp_value = value.replace('$$', '')  # escaped dollar signs
        if '$' in tmp_value:
            raise ValueError("invalid interpolation syntax in %r at "
                             "position %d" % (value, tmp_value.find('$')))
        return value

    def _interpolate_some(self, parser, option, accum, rest, section, map,
                          depth):
        if depth > confp.MAX_INTERPOLATION_DEPTH:
            raise confp.InterpolationDepthError(option, section, rest)
        while rest:
            p = rest.find("$")
            if p < 0:
                accum.append(rest)
                return
            if p > 0:
                accum.append(rest[:p])
                rest = rest[p:]
            # p is no longer used
            c = rest[1:2]
            if c == "$":
                accum.append("$")
                rest = rest[2:]
            elif c == "{":
                m = self._KEYCRE.match(rest)
                if m is None:
                    msg = ("bad interpolation variable reference"
                           " {}".format(rest))
                    raise confp.InterpolationSyntaxError(option, section, msg)
                path = m.group(1).split(':')
                rest = rest[m.end():]
                sect = section
                opt = option
                try:
                    if len(path) == 1:
                        opt = parser.optionxform(path[0])
                        v = map[opt]
                    elif len(path) == 2:
                        sect = path[0]
                        opt = parser.optionxform(path[1])
                        v = parser.get(sect, opt, raw=True)
                    else:
                        raise confp.InterpolationSyntaxError(
                            option, section,
                            "More than one ':' found: %r" % (rest,))
                except (KeyError, confp.NoSectionError,
                        confp.NoOptionError):
                    raise confp.InterpolationMissingOptionError(
                        option, section, rest, ":".join(path))
                if "$" in v:
                    self._interpolate_some(parser, opt, accum, v, sect,
                                           dict(parser.items(sect, raw=True)),
                                           depth + 1)
                else:
                    accum.append(v)
            else:
                raise confp.InterpolationSyntaxError(
                    option, section,
                    "'$' must be followed by '$' or '{', "
                    "found: %r" % (rest,))

# Register interpolators in six.moves
# === attributes

# add them to six.moves
six.add_move(six.MovedAttribute("BasicInterpolation",
                                "pyhetdex.tools.configuration",
                                "configparser"))
six.add_move(six.MovedAttribute("ExtendedInterpolation",
                                "pyhetdex.tools.configuration",
                                "configparser"))
