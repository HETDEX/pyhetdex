# Misc python library to support HETDEX software and data analysis
# Copyright (C) 2015  "The HETDEX collaboration"
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
"""Docstring manipulation tools
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def format_docstring(*args, **kwarg):
    """Decorator to allow string formating in docstrings using `Format string
    syntax
    <https://docs.python.org/3.4/library/string.html#format-string-syntax>`_

    Examples
    --------

    .. testsetup:: *

        from pyhetdex.doc.docstring import format_docstring

    >>> @format_docstring(a=10, b="hi")
    ... def foo():
    ...    "I want to say '{b}' {a} times"
    ...    pass
    >>> foo.__doc__
    "I want to say 'hi' 10 times"
    """
    def wrapper(func):
        doc = func.__doc__
        doc = doc.format(*args, **kwarg)
        func.__doc__ = doc
        return func
    return wrapper
