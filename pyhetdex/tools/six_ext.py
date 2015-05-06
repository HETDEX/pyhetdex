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
