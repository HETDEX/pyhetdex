from __future__ import absolute_import

from astropy.table import Table


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


def read_daophot(fn):
    """Read in a DAOPHOT ALLSTAR file from a run on a collapsed cube/apimage
    file

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
    table = Table.read(fn, format='ascii', data_start=2,
                       names=['ID', 'icx', 'icy', 'mag', 'mag_std', 'sky',
                              'niter', 'CHI', 'SHARP'])

    # transform to system where 0,0 is at center of IFU
    return table['icx'] - 24.5, table['icy'] - 24.5, table
