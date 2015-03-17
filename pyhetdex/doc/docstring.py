"""Docstring manipulation tools
"""


def format_docstring(*args, **kwarg):
    """Decorator to allow string formating in docstrings using `Format string
    syntax
    <https://docs.python.org/3.4/library/string.html#format-string-syntax>`_

    Examples
    --------
    >>> @format_docstring(a=10, b="hi")
    >>> def foo():
    ...    "I want to say '{b}' {a} times"
    ...    pass
    >>> help(foo)
    foo()
        I want to say 'ciao' 10 times
    """
    def wrapper(func):
        doc = func.__doc__
        doc = doc.format(*args, **kwarg)
        func.__doc__ = doc
        return func
    return wrapper
