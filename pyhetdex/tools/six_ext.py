"""Extensions to ``six`` python 2 and 3 compatibility layer.

"""

import six

# === Exception definitions
if six.PY3:
    FileOpenError = FileNotFoundError
    """File not found"""
    SubprocessExeError = FileNotFoundError
    """:class:`subprocess.Popen` does not find the file to execute"""
    ConfigFileError = FileNotFoundError
    """Configuration file not found"""
else:
    FileOpenError = IOError
    """File not found"""
    SubprocessExeError = OSError
    """:class:`subprocess.Popen` does not find the file to execute"""

    class ConfigFileError(OSError):
        """Configuration file not found"""
        pass

# === module definitions
mock = six.MovedModule("mock", "mock", "unittest.mock")
"""This is to be imported as a standard module.

Examples
--------
>>> from pyhetdex.tools.six_ext import mock
>>> # or if :mod:`~pyhetdex.tools.six_ext` has already been imported somewhere
>>> # in the code
>>> from six.moves import mock
"""
six.add_move(mock)  # move to six.moves
