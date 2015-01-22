"""
Anything related with the HETDEX IFUCenter files should go here
"""
from __future__ import print_function, absolute_import

from collections import defaultdict

import pyhetdex.common.file_tools as ft


class IFUCenterError(ValueError):
    pass


class IFUCenter(object):
    """
    Parse the IFU center file
    """
    def __init__(self, ifu_center_file):
        """
        Parse the IFU center file and store the relevant information
        Parameters
        ----------
        ifu_center_file: string
            file containing the fiber positions in the IFU.
        """
        # these constitute the public interface
        self.filename = ifu_center_file
        self.fiber_d = 0.
        self.fiber_sep = 0.
        self.nfibx, self.nfiby = 0, 0
        self.xifu, self.yifu = defaultdict(list), defaultdict(list)
        self.n_fibers = defaultdict(int)
        self.fib_number = defaultdict(list)
        self.throughput = defaultdict(list)

        self._read_ifu(ifu_center_file)

    def _read_ifu(self, ifu_center_file):
        """
        Read the ifu center file
        Parameters
        ----------
        ifu_center_file: string
            file containing the fiber number to fiber position mapping
        """
        with open(ifu_center_file, 'r') as f:
            # get the fiber diameter and fiber separation
            f = ft.skip_comments(f)
            line = f.readline()
            self.fiber_d, self.fiber_sep = [float(i) for i in line.split()]
            # get the number of fibers in the x and y direction
            f = ft.skip_comments(f)
            line = f.readline()
            self.nfibx, self.nfiby = [int(i) for i in line.split()]
            # get from the rest of the file:
            # the fiber position (second and third column)
            # target unit spectrograph (L or R) (fourth column)
            # target fiber within the spectrograph (fifth column)j
            # relative throughput (sixth column)
            f = ft.skip_comments(f)
            f = self._read_ifu_map(f)

    # TODO: check carefully definition of failed fibers to adjust the
    # acceptance or failure
    def _read_ifu_map(self, f):
        """
        Reads and store the remaining part of the file. Each row is expected to
        be like:
        ID        x ["]       y ["]    channel  fiber number        throughput
                                                on spectrograph
        0001      -22.88      -24.24   L (or R) 0001                1.000

        The first column is ignored, the number of L or R is counted, the x, y
        and fiber numbers are saved in lists stored in dictionaries with L or R
        as keys. The throughput is used as check. Missing fibers are indicated
        by negative fiber numbers or non integer values (like 'nan', '-', etc)
        A ValueError is raised if a fiber number is positive and the throughput
        zero
        Parameters
        ----------
        f: file object
        output
        ------
        f: file object
            moved to the next non comment line
        """
        for line in f:
            if line.startswith('#'):
                continue
            _x, _y, _channel, _fib_n, _t = line.split()[1:6]
            # convert the fiber number to integer. If fails, means that the
            # fiber is broken
            try:
                _fib_n = int(_fib_n)
            except ValueError:
                continue

            if _fib_n > 0:
                if float(_t) < 0.01:  # zero or less
                    msg = 'In the fiber mapping file there is at least one'
                    msg += ' fiber with positive fiber number and 0 throughput'
                    msg += '. What should I do?'
                    raise IFUCenterError(msg)
                else:
                    self.n_fibers[_channel] += 1
                    self.xifu[_channel].append(float(_x))
                    self.yifu[_channel].append(float(_y))
                    self.fib_number[_channel].append(_fib_n)
                    self.throughput[_channel].append(float(_t))

    @property
    def channels(self):
        """
        list of channels
        output
        ------
        channels: list of strings
        """
        return list(self.n_fibers.keys())
