"""Extensions to ``six`` python 2 and 3 compatibility layer.

"""

import six

# === Exception definitions
if six.PY3:
    FileOpenError = FileNotFoundError
    SubprocessExeError = FileNotFoundError
else:
    FileOpenError = IOError
    SubprocessExeError = OSError
