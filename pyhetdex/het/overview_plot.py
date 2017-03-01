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


class OverviewPlotError(Exception):
    pass


class OverviewPlot(object):
    '''Documentation goes here!


    '''

    def __init__(self):
        self.fig = plt.figure(figsize=(20, 20))
        self.zmin = None
        self.zmax = None
        self.lastplot = None

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
        sp = self.fig.add_subplot(10, 12, self._slot_to_plot(ifuslot))
        sp.set_xticks([])
        sp.set_yticks([])

        pltarray = None

        for f in files:
            hdu = fits.open(f)
            data = hdu[0].data
            xoff = 0
            yoff = 0
            if hdu[0].header['CCDPOS'] == 'R':
                xoff = data.shape[0]
            if hdu[0].header['CCDHALF'] == 'U':
                yoff = data.shape[1]

            if pltarray is None:
                pltarray = np.zeros((data.shape[0]*2,
                                     data.shape[1]*2))

            pltarray[xoff:xoff+data.shape[0],
                     yoff:yoff+data.shape[1]] = data

            if self.zmin is None:
                zscale = ZScaleInterval()
                self.zmin, self.zmax = zscale.get_limits(pltarray)

            self.lastplot = sp.imshow(pltarray, cmap='Greys',
                                      clim=(self.zmin, self.zmax),
                                      origin='lower')

    def _add_cmap(self):
        '''Add the colormap
        '''
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
        '''
        self._add_cmap()
        plt.suptitle(title, fontsize=18)
        plt.savefig(fname)

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
