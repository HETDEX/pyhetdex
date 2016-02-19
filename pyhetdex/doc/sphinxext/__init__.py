from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import warnings

msg = ("The module '{name}' and '{name}.todo' have been deprecated and will"
       "be removed in future releases. The modifications to the ``todo``"
       " have been integrated into sphinx.ext.todo and have been released as"
       " part of sphinx 1.4.").format(name=__name__)

with warnings.catch_warnings():
    warnings.simplefilter("always")
    warnings.warn(msg, DeprecationWarning)
