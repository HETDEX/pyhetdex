# Misc python library to support HETDEX software and data analysis
# Copyright (C) 2016, 2017  "The HETDEX collaboration"
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import absolute_import

from numpy import concatenate, chararray
from astropy.table import Table
from pyhetdex.het.ifu_centers import IFUCenter


def read_ifu_cen_wrapper(fn):
    """
    A wrapper for het.IFUCenter that produces an
    output compatible with the astrometry routines

    Parameters
    ----------
    fn : str
        the IFU cen file to read

    Returns
    -------
    x, y : array
        the x, y coordinates of the fibers
    table : astropy.table.Table
        the IFU cen file info in the form of a table
    """

    ifu_cen = IFUCenter(fn)

    if ("L" in ifu_cen.xifu.keys()) and ("R" in ifu_cen.yifu.keys()):
        x = concatenate((ifu_cen.xifu["L"], ifu_cen.xifu["R"]))
        y = concatenate((ifu_cen.yifu["L"], ifu_cen.yifu["R"]))

        channel = chararray((len(ifu_cen.xifu["L"]) + len(ifu_cen.xifu["R"])))
        channel[:len(ifu_cen.xifu["L"])] = "L"
        channel[len(ifu_cen.xifu["L"]):] = "R"

        fib_number = concatenate((ifu_cen.fib_number["L"],
                                  ifu_cen.fib_number["R"]))

    elif "R" in ifu_cen.xifu.keys():
        x = ifu_cen.xifu["R"]
        y = ifu_cen.xifu["R"]
        fib_number = ifu_cen.fib_number["R"]
        channel = chararray((len(ifu_cen.xifu["R"])))
        channel[:] = "R"

    elif "L" in ifu_cen.xifu.keys():
        x = ifu_cen.xifu["L"]
        y = ifu_cen.xifu["L"]
        fib_number = ifu_cen.fib_number["L"]
        channel = chararray((len(ifu_cen.xifu["L"])))
        channel[:] = "L"
    else:
        raise Exception("No channels found in IFUcen file!")

    return x, y, Table([channel, fib_number], names=["channel", "fib_number"])


def read_matched_line_detect(fn):
    """Read in line detect file matched to a simsrc input file

    Parameters
    ----------
    fn : str
        the filename to read

    Returns
    -------
    x, y : array
        the x, y coordinates from the file
    table : astropy.table.Table
        the rest of the table
    """
    table = Table.read(fn, format='ascii',
                       names=('ID_in', 'xin', 'yin', 'l_rest', 'flux_in',
                              'zin', 'NR', 'ID', 'XS', 'YS', 'l', 'z',
                              'dataflux', 'modflux', 'fluxfrac', 'sigma',
                              'chi2', 'chi2s', 'chi2w', 'gammq', 'gammq_s',
                              'eqw',  'cont',  'separation'))
    return table['xin'], table['yin'], table


def read_simsrc_in(fn):
    """Read in a simsrc input file

    Parameters
    ----------
    fn : str
        the filename to read

    Returns
    -------
    x, y : array
        the x, y coordinates from the file
    table : astropy.table.Table
        the rest of the table
    """
    table = Table.read(fn, format='ascii', comment='#',
                       names=('ID', 'xin', 'yin', 'l_rest', 'flux_in', 'zin'))

    return table['xin'], table['yin'], table


def read_line_detect(fn):
    """Read in a line file from detect

    Parameters
    ----------
    fn : str
        the filename to read

    Returns
    -------
    x, y : array
        the x, y coordinates from the file
    table : astropy.table.Table
        the rest of the table
    """
    table = Table.read(fn, format='ascii', comment='#',
                       names=('NR', 'ID', 'XS', 'YS', 'l', 'z', 'dataflux',
                              'modflux', 'fluxfrac', 'sigma', 'chi2', 'chi2s',
                              'chi2w', 'gammq', 'gammq_s', 'eqw',  'cont'))

    return table['XS'], table['YS'], table


def read_cont_detect(fn):
    """Read in a cont file from detect

    Parameters
    ----------
    fn : str
        the filename to read

    Returns
    -------
    x, y : array
        the x, y coordinates from the file
    table : astropy.table.Table
        the rest of the table
    """
    table = Table.read(fn, format='ascii', comment='#',
                       names=('ID', 'icx', 'icy', 'sigma', 'fwhm_xy', 'a',
                              'b', 'pa', 'ir1', 'ka', 'kb',  'xmin', 'xmax',
                              'ymin', 'ymax', 'zmin', 'zmax'))

    return table['icx'], table['icy'], table


def read_daophot(fn, xoff=-26.15, yoff=-26.24):
    """Read in a DAOPHOT ALLSTAR file from a run on a collapsed cube/apimage
    file

    Parameters
    ----------
    fn : str
        the filename to read
    xoff, yoff : float
        offsets to add to the x, y positions
        in the catalogue to correct them to the
        detect coordinate system.

    Returns
    -------
    x, y : array
        the x, y coordinates from the file
    table : astropy.table.Table
        the rest of the table
    """
    table = Table.read(fn, format='ascii', data_start=2,
                       names=['ID', 'icx', 'icy', 'mag', 'mag_std', 'sky',
                              'niter', 'CHI', 'SHARP'])

    # transform to system where 0,0 is at center of IFU
    return table['icx'] + xoff, table['icy'] + yoff, table
