# Misc python library to support HETDEX software and data analysis
# Copyright (C) 2017, 2018  "The HETDEX collaboration"
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
'''Create an overview plot showing thumbnails for all raw images in
one virus exposure. All thumbnails are created using the zscale algorithm
and using the same min / max values as the first generated subplot.

To use, first create a OverviewPlot object, then run add_plot for
every ifuslot, with 4 filenames, and finally save_plot with the output filename

Attributes
----------
fig : :py:class:`~matplotlib.Figure`
   The plot figure object
zmin : float
   The minimum value for the image scaling
zmax : float
   The maximum value for the image scaling
lastplot : :py:class:`~matplotlib.Axes`
   The last generated subplot, used for the colormap plot
'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.visualization import ZScaleInterval
from astropy.stats import sigma_clip

from pyhetdex.tools.files.fits_tools import parse_fits_region


class OverviewPlotError(Exception):
    pass


class OverviewPlot(object):
    '''Documentation goes here!


    '''

    def __init__(self):
        self._ready = True
        self._saved = False
        self.fig = plt.figure(figsize=(20, 20))
        self.zmin = None
        self.zmax = None
        self.lastplot = None

    def _check_ready(self):
        if not self._ready:
            raise Exception('The plot was already closed!')

    def add_plot(self, files, ifuslot):
        '''
        Add another subplot.

        Parameters
        ----------
        files : list
            List of four filenames to be plotted
        ifuslot : str
            IFUSlot name, used to find the correct subplot position
        '''
        self._check_ready()

        sp = self.fig.add_subplot(10, 12, self._slot_to_plot(ifuslot))
        sp.set_xticks([])
        sp.set_yticks([])

        pltarray = None

        for f in files:
            with fits.open(f) as hdu:
                data = hdu[0].data
                xoff = 0
                yoff = 0

                biassec = parse_fits_region(hdu[0].header['BIASSEC'])
                trimsec = parse_fits_region(hdu[0].header['TRIMSEC'])

                ovsc = data[biassec[2]-1:biassec[3]-1,
                            biassec[0]-1:biassec[1]-1]
                imdata = data[trimsec[2]-1:trimsec[3]-1,
                              trimsec[0]-1:trimsec[1]-1]

                imdata = imdata.astype(float)
                imdata -= np.average(sigma_clip(ovsc, sigma=2.8))

                if hdu[0].header['CCDPOS'] == 'R':
                    xoff = imdata.shape[0]
                if hdu[0].header['CCDHALF'] == 'U':
                    yoff = imdata.shape[1]

                if pltarray is None:
                    pltarray = np.zeros((imdata.shape[0]*2,
                                        imdata.shape[1]*2))

                pltarray[xoff:xoff+imdata.shape[0],
                         yoff:yoff+imdata.shape[1]] = imdata

            del hdu[0].data
            del data
            del ovsc
            del imdata

        if self.zmin is None:
            zscale = ZScaleInterval()
            self.zmin, self.zmax = zscale.get_limits(pltarray)

        sp.set_title('%s' % hdu[0].header['IFUSLOT'])
        self.lastplot = sp.imshow(pltarray, cmap='Greys',
                                  clim=(self.zmin, self.zmax),
                                  origin='lower')

        del pltarray

    def _add_cmap(self):
        '''Add the colormap
        '''
        self._check_ready()

        if self.lastplot is None:
            return
        self.fig.subplots_adjust(right=0.8)
        cbar_ax = self.fig.add_axes([0.85, 0.15, 0.05, 0.7])
        self.fig.colorbar(self.lastplot, cax=cbar_ax)

    def save_plot(self, fname, title=''):
        '''Save the figure to file

        Parameters
        ----------
        fname : str
            The filename used for saving
        title : str, optional
            An optional plot title

        If this function is called a second time, the plot title won't be
        changed, and the file only saved again
        '''
        self._check_ready()

        if not self._saved:
            self._add_cmap()
            plt.suptitle(title, fontsize=18)
            plt.draw()
        plt.savefig(fname)
        self._saved = True

    def close(self):
        if self._ready:
            plt.clf()
            plt.close(self.fig)
            self.fig = None
            self._ready = False

    def _slot_to_plot(self, ifuslot):
        '''Convert the ifuslot string into
        the plot number for add_subplot

        Parameters
        ----------
        ifuslot : str
            IFUSlot name
        '''
        col = int(ifuslot[0:2])
        row = int(ifuslot[2:])

        return col + row*12 + 1
