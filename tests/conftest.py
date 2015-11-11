"""pytest configurations and global stuff"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import matplotlib
matplotlib.use('Agg')

collect_ignore = ["setup.py"]
