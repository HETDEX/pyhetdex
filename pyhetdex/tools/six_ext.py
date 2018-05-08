# Misc python library to support HETDEX software and data analysis
# Copyright (C) 2015, 2017  "The HETDEX collaboration"
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
