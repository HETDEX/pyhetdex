"""pytest configurations and global stuff"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import matplotlib
matplotlib.use('Agg')

import pytest
import py
import os

collect_ignore = ["setup.py"]


@pytest.fixture
def datadir():
    """ Return a py.path.local object for the test data directory"""
    return py.path.local(os.path.dirname(__file__)).join('data')
