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
