"""Parse and manipulation of the IFU center files with the following structure

::

    # HETDEX IFU description file
    # $Id: IFUcen_HETDEX.txt 789 2012-08-17 19:52:17Z mxhf $
    #
    # IFU 00001
    #
    # Test date: YYYYMMDD
    # Total number of dead fibers (T < X %):
    #
    #
    # history
    # date     author   change
    # -------------------------
    # 20110702 mF       created
    #
    #
    # FIBERD   FIBERSEP
    1.55      2.20
    # NFIBX NFIBY
    20 23
    #
    # col 1: fiber ID, starts with 1, IDs 1-246 belong to left unit, 247-492 belong to right unit
    # col 2: fiber x position ["]
    # col 3: fiber y position ["]
    # col 4: target unit spectrograph L=left, R=right
    # col 5: target fiber within the spectrograph, fiber numbers start with 1 within each spectrograph
    # col 6: relative throughput at fiducial wavelength
    #
    0001  -19.8000  -19.6876 L 0001    1.000
    0002  -17.6000  -19.6876 L 0002    1.000
    [...]
    0447   17.6000   19.6876 R 0223    1.000
    0448   19.8000   19.6876 R 0224    1.000

From the header the ``FIBERD``, ``FIBERSEP``, ``NFIBX`` and ``NFIBY`` are
extracted. The rest of the file is parsed as follow:

* the number of ``L`` or ``R`` are counted;
* the columns number 2, 3, 5 and 6 are stored in dictionaries with the
    channels as keys;
* a row is ignored if:
    1. it starts with ``#``;
    2. the target fiber number is negative or cannot be converted to an
        integer (e.g. ``nan``, ``--``);
* if the throughput if a valid fiber is less than ``0.01`` a
    :class:`IFUCenterError` is raised as such a fiber should be ignored.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from collections import defaultdict

import pyhetdex.tools.files.file_tools as ft


class IFUCenterError(ValueError):
    "Exception raised when the IFU center file parsing fails"
    pass


class IFUCenter(object):
    """Parse the IFU center file

    Parameters
    ----------
    ifu_center_file : string
        file containing the fiber positions in the IFU.

    Attributes
    ----------
    filename : string
        name of the IFU center file
    fiber_d : float
        fiber diameter
    fiber_sep : float
        fiber separation
    nfibx, nfiby : int
        number of fibers in the x and y directions
    xifu, yifu : dictionary of lists
        fibers x and y positions per channel
    n_fibers : dictionary of int
        number of fibers per channel
    fib_number : dictionary of lists
        fiber number corresponding to positions ``xifu``, ``yifu`` per channel
    throughput : dictionary of lists
        throughput corresponding to positions ``xifu``, ``yifu`` per channel

    Raises
    ------
    IFUCenterError
        if it cannot decide whether a fibers must be used or not
    """
    def __init__(self, ifu_center_file):
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
        """Read the ifu center file

        Parameters
        ----------
        ifu_center_file : string
            file containing the fiber number to fiber position mapping
        """
        with open(ifu_center_file, 'r') as f:
            f = self._read_header(f)
            f = self._read_ifu_map(f)

    def _read_header(self, f):
        """
        Parameters
        ----------
        f : file object
            file object to parse

        Returns
        -------
        f : file object
            file object after consuming the header
        """
        # get the fiber diameter and fiber separation
        f = ft.skip_comments(f)
        line = f.readline()
        self.fiber_d, self.fiber_sep = [float(i) for i in line.split()]
        # get the number of fibers in the x and y direction
        f = ft.skip_comments(f)
        line = f.readline()
        self.nfibx, self.nfiby = [int(i) for i in line.split()]
        f = ft.skip_comments(f)
        return f

    # TODO: check carefully definition of failed fibers to adjust the
    # acceptance or failure
    def _read_ifu_map(self, f):
        """
        Parameters
        ----------
        f : file object
            file to parse

        Returns
        -------
        f : file object
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
        return f

    @property
    def channels(self):
        """
        list of channels
        """
        return list(self.n_fibers.keys())
