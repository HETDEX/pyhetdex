"""Extensions to ``six`` python 2 and 3 compatibility layer.

The following exceptions are more descriptive aliases to python 3 or python 2
exceptions.

.. list-table:: Exceptions
    :header-rows: 1
    :widths: 1 1 1 1

    * - Name
      - Python 3 name
      - Python 2 name
      - Description
    * - :exc:`FileOpenError`
      - :exc:`FileNotFoundError`
      - :exc:`IOError`
      - File not found
    * - :exc:`SubprocessExeError`
      - :exc:`FileNotFoundError`
      - :exc:`OSError`
      - :class:`subprocess.Popen` does not find the file to execute
    * - :exc:`ConfigFileError`
      - :exc:`FileNotFoundError`
      - :exc:`OSError`
      - Configuration file not found

The module also provided some modules renamed as described in the `six
documentation <https://pythonhosted.org/six/#module-six.moves>`_.

.. list-table:: Renamed modules
    :header-rows: 1

    * - Name
      - Python 3 name
      - Python 2 name
    * - mock
      - unittest.mock
      - mock

Example of used of renamed modules

>>> from pyhetdex.tools.six_ext import mock
>>> # or if :mod:`~pyhetdex.tools.six_ext` has already been imported somewhere
>>> # in the code
>>> from six.moves import mock  # doctest: +SKIP
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six

# === Exception definitions
if six.PY3:
    FileOpenError = FileNotFoundError
    SubprocessExeError = FileNotFoundError
    ConfigFileError = FileNotFoundError
else:
    FileOpenError = IOError
    SubprocessExeError = OSError

    class ConfigFileError(OSError):
        """Configuration file not found"""
        pass

# === module definitions
mock = six.MovedModule("mock", "mock", "unittest.mock")
six.add_move(mock)  # move to six.moves
