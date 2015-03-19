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

Examples
--------
>>> # python2
>>> import pyhetdex.tools.configuration as pconf
>>> # standard config parser interpolation
>>> stdparser = pconf.ConfigParser()
>>> # extended config parser interpolation
>>> extparser = pconf.ConfigParser(interpolation=pconf.ExtendedInterpolation())

>>> # python3
>>> import pyhetdex.tools.configuration as pconf
>>> from configparser import ExtendedInterpolation
>>> # standard config parser interpolation
>>> stdparser = pconf.ConfigParser()
>>> # extended config parser interpolation
>>> extparser = pconf.ConfigParser(interpolation=ExtendedInterpolation())

>>> # Configuration file: default interpolation
>>> [general]
>>> dir1 = /path/to
>>> [section]
>>> dir1 = /path/to
>>> file1 = %(dir1)/file1

>>> # Configuration file: extended interpolation
>>> [general]
>>> dir1 = /path/to
>>> [section]
>>> file1 = %{general:dir1}/file1
"""

from __future__ import absolute_import, print_function

import ast
try:  # python 2.x
    import ConfigParser as confp
except ImportError:  # python 3.x
    import configparser as confp
import re


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

    def get_list_of_list(self, section, option, use_default=False):
        """
        A convenience method which coerces the option in the specified section
        to a list of lists.

        Examples
        --------
        ::

            >>> cat settings.cfg:
            [section]
            wranges_bkg = 3500-4500,4500-5500
            >>> conf.get_list_of_list("section", "wranges_bkg")
            [[3500, 4500], [4500, 5500]]

            >>> cat settings.cfg:
            [section]
            >>> conf.get_list_of_list("section", "wranges_bkg")
            NoOptionError
            >>> conf.get_list_of_list("section", "wranges_bkg", default=True)
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
            value = value.split(',')  # divide the various groups
            # split each of the '-' separated couples and convert to float
            value = [list(map(float, i.split('-'))) for i in value]
            return value
        except confp.NoOptionError:
            if use_default:
                return [[None, None]]
            else:
                raise

    def get_list(self, section, option, use_default=False):
        """
        A convenience method which coerces the option in the specified section
        to a list

        Examples:
        ::

            >>> cat settings.cfg:
            [section]
            wranges_iq = 3500, 4500, 5500
            literal_list = ['a', 'b', 'c']
            >>> conf.get_list_of_list("section", "wranges_bkg")
            [3500, 4500, 5500]
            >>> conf.get_list_of_list("section", "literal_list")
            ['a', 'b', 'c']

        Parameters
        ----------
        section : string
            name of the section
        option : string
            name of the option
        use_default : bool
            whether default to ``[]``

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
            return list(ast.literal_eval(value))
        except ValueError:  # ValueError: malformed string
            # e.g. "a, b, c" which is valid cannot be converted into a list of
            # strings. So if this happens simply split the value on commas,
            # strip and return it
            values = value.split(',')
            return [v.strip() for v in values]
        except confp.NoOptionError:
            if use_default:
                return []
            else:
                raise

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
                    raise confp.InterpolationSyntaxError(option, section,
                            "bad interpolation variable reference %r" % rest)
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
                    raise confp.InterpolationSyntaxError(option, section,
                            "bad interpolation variable reference %r" % rest)
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
