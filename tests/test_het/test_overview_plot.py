"""
Test the overview plotting
"""
from __future__ import (absolute_import, division, print_function)

import pyhetdex.het.overview_plot as op
import os

inputfilenames_l = ['20151025T122555_103LL_sci.fits',
                    '20151025T122555_103LU_sci.fits']

inputfilenames_r = ['20151025T122555_103RL_sci.fits',
                    '20151025T122555_103RU_sci.fits']

inputfilenames = inputfilenames_l + inputfilenames_r


def test_overview_plot(datadir, tmpdir):

    infiles = [datadir.join(i).strpath for i in inputfilenames]
    outfile = tmpdir.join('oplot.pdf').strpath

    oplot = op.OverviewPlot()
    oplot.add_plot(infiles, '103')
    oplot.add_plot(infiles, '104')
    oplot.save_plot(outfile, 'Testplot')

    assert os.path.exists(outfile)


def test_empty_overview_plot(datadir, tmpdir):

    infiles = [datadir.join(i).strpath for i in inputfilenames]
    outfile = tmpdir.join('oplot.pdf').strpath

    oplot = op.OverviewPlot()
    oplot.save_plot(outfile, 'Testplot')

    assert os.path.exists(outfile)
