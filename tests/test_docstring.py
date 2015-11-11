"""Test pyhetdex/doc/docstring.py"""

from pyhetdex.doc.docstring import format_docstring


def test_format_docstring():
    @format_docstring(a=10, b="hi")
    def foo():
        "I want to say '{b}' {a} times"
        pass

    assert foo.__doc__ == "I want to say 'hi' 10 times"
