"""Test pyhetdex/doc/docstring.py"""

import nose.tools as nt

from pyhetdex.doc.docstring import format_docstring


def test_format_docstring():
    @format_docstring(a=10, b="hi")
    def foo():
        "I want to say '{b}' {a} times"
        pass

    nt.assert_equal(foo.__doc__, "I want to say 'hi' 10 times")
