"""Configuration set up
"""
from __future__ import absolute_import, print_function

import ast
try:  # python 2.x
    import ConfigParser as confp
except ImportError:  # python 3.x
    import configparser as confp


# =============================================================================
# Custom configuration parser. Provides extra get methods to parse and store
# complex options
# =============================================================================
class ConfigParser(confp.ConfigParser):
    """Customise configuration parser
    """

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
