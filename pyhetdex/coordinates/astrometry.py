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
""" Astrometry module

Module to add astrometry to HETDEX catalgoues and images


.. moduleauthor:: Daniel Farrow <dfarrow@mep.mpg.de>
"""

from __future__ import (absolute_import, print_function)
import re
import os.path as op
import sys
import argparse
import astropy.units as units
from numpy import float64, fabs
from astropy.io.fits import getheader, getdata, PrimaryHDU
from astropy.table import Table, vstack, hstack
from astropy.coordinates import SkyCoord, FK5
import pyhetdex.tools.read_catalogues as rc
from pyhetdex.het.fplane import FPlane
from pyhetdex.coordinates.tangent_projection import TangentPlane


# common parts of the argument parser
astro_parent = argparse.ArgumentParser(add_help=False)
_group_astro = astro_parent.add_mutually_exclusive_group()
_group_astro.add_argument('--astrometry', nargs=3, type=float64,
                          help='''RA DEC and PA of the focal plane center
                          (degrees)''')
_group_astro.add_argument('--image', help='''An image, with a header to grab
                          ra, dec and PA from (DONT USE THIS)''')
astro_parent.add_argument('--rhozp', default=0.0, type=float,
                          help='''Optionally set the rho zeropoint in degrees, i.e. the
                          rotation of the IHMP wrt HET (default=0.0 deg)''')


def ihmp_astrometry(opts, xscale=1.0, yscale=1.0):
    """
    Set up a tangent plane projection from
    parsed command line arguments from ArgParse

    Parameters
    ----------
    opts :
        command line options, either 'image' for a fits file with TELRA,
        TELDEC, PARANGLE, MJD or and 'astrometry' option to manually specify
        coordinates
    xscale, yscale : float
        number of arcseconds per pixel for the WCS header created (default 1,1)

    Returns
    -------
    tp : pyhetdex.coordinates.tangent_projection.TangentPlane
        tangent plane object to use for astrometry
    """
    if opts.image:
        raise Exception("Don't use this option, the header values aren't"
                        " accurate enough")
        # Set up astrometry using the values in the header
        print("Reading header values from {:s}".format(opts.image))
        head = getheader(opts.image)
        rastr = head['TELRA']
        decstr = head['TELDEC']
        # empirical offset between PARANGLE and rotation
        pa = head['PARANGLE'] + 1.6

        # convert from local equinox to J2000
        equinox = 2016 + (head['MJD'] - 57388)/365.24
        gc = SkyCoord(rastr, decstr, unit=(units.hourangle, units.deg),
                      frame='fk5', equinox='J{:0.4f}'.format(equinox))
        s = gc.transform_to(FK5(equinox='J2000.0'))

        # From Majo (with a bit of tweaking)
        TELRA = 0.002414529  # 0.0018589733
        TELDEC = -0.00307875  # -0.0033565244

        print(s.ra.deg + TELRA, s.dec.deg + TELDEC, pa)
        tp = TangentPlane(s.ra.deg + TELRA, s.dec.deg + TELDEC, pa,
                          x_scale=xscale, y_scale=yscale)
    else:
        # Carry out required changes to astrometry
        rot = 360.0 - (opts.astrometry[2] + 90. + opts.rhozp)

        # Set up astrometry from user supplied options
        tp = TangentPlane(opts.astrometry[0], opts.astrometry[1], rot)

    return tp


def ra_dec_to_xy(ra, dec, fplane, tp):
    """Given ras and a decs, return a table of x, y of the nearest IFU, x and
    y in the focal plane and IFU slot of nearest IFU

    Parameters
    ----------
    ra, dec : float arrays
        ra and dec on objects in decmal degrees
    fplane : pyhetdex.het.fplane:FPlane class
        an instance of the focal plane class
    tp : pyhetdex.coordinates.tangent_projection:TangentPlane
        a tangent plane that converts ra, dec to the appropriate x,y in axes
        aligned with the IFU axes

    Returns
    -------
    table : astropy.table:Table
        an astropy table containing the positions in the IFUs
    """

    """
    Get x, y in arcseconds in the focal plane (using the IFU coordinates, i.e.
    flipped wrt to the fplane file)
    """
    x, y = tp.raDec2xy(ra, dec)

    # fill in output with dummy values
    table = Table([[999.0]*len(ra), [999.0]*len(ra), [999]*len(ra)],
                  names=['xifu', 'yifu', 'ifuslot'])

    # loop over IFUs computing coordinates
    for ifu in fplane.ifus:

        # remember to swap x and y for this (inverse of the x,y to ra, dec)
        xt = x - ifu.y
        yt = y - ifu.x

        # Find out table if an object is in IFU (set this a bit larger to avoid
        # edge effects)
        indices = (fabs(x - ifu.y) < 30) & (fabs(y - ifu.x) < 30)

        (table['xifu'])[indices] = xt[indices]
        (table['yifu'])[indices] = yt[indices]
        (table['ifuslot'])[indices] = ifu.ifuslot

    return table


def add_ifu_xy(args=None):
    """Convert ra, dec to x, y in an IFU.

    Parameters
    ----------
    args : list of strings, optional
        command line
    """
    parser = argparse.ArgumentParser(description="""Convert between ra, dec to
                                     IFU x, y. Note that currently anything
                                     within +/- 30 arcseconds of the IFU is
                                     output. If IFUs overlap the detection will
                                     only be output for one of them""",
                                     parents=[astro_parent, ])

    parser.add_argument('file', type=str,
                        help="A csv or fits file with ra and dec columns")

    parser.add_argument('fout', type=str,
                        help="""A csv or fits file to output to (including
                        extension: .fits or .csv)""")

    parser.add_argument('--ra-name', type=str, help="""The label of the ra
                        column in the input""", default='ra')

    parser.add_argument('--dec-name', type=str, help="""The label of the dec
                        column in the input""", default='dec')

    parser.add_argument('--fplane', default='fplane.txt',
                        help='Focal plane file')

    opts = parser.parse_args(args)

    # Verify user input
    if not (opts.image or opts.astrometry):
        print("""Error: Either pass an image with TELRA, TELDEC, PARANGLE and
              MJD in the header, or manually specify raccen, deccen and PA with
              the astrometry option""")
        sys.exit(1)

    # set up astrometry
    fplane = FPlane(opts.fplane)
    tp = ihmp_astrometry(opts)

    # read in catalogue
    table_in = Table.read(opts.file)
    ra = table_in[opts.ra_name]
    dec = table_in[opts.dec_name]

    # find positions
    table_out = ra_dec_to_xy(ra, dec, fplane, tp)

    # save data
    table_final = hstack([table_in, table_out])

    table_final.write(opts.fout)


def xy_to_ra_dec(args=None):
    """ Convert between x y within an IFU and ra, dec

    Parameters
    ----------
    args : list of strings, optional
        command line
    """
    parser = argparse.ArgumentParser(description="Convert between in-IFU x, y"
                                     " and on-sky ra, dec.",
                                     parents=[astro_parent, ])

    parser.add_argument('pos', type=float64, nargs=2,
                        help="""Position in IFU (w.r.t. to IFU position in
                        fplane file, i.e. the IFU center)""")
    parser.add_argument('--fplane', default='fplane.txt',
                        help='Focal plane file')

    # astrometry options

    # IHMP identification
    parser.add_argument('--ihmp', nargs=1, help='IFU slot of desired IFU')

    opts = parser.parse_args(args)

    # Verify user input
    if not (opts.image or opts.astrometry):
        print("""Error: Either pass an image with TELRA, TELDEC, PARANGLE and
              MJD in the header, or manually specify raccen, deccen and PA with
              the astrometry option""")
        sys.exit(1)

    fplane = FPlane(opts.fplane)
    tp = ihmp_astrometry(opts)

    ifu = fplane.by_ifuslot(opts.ihmp[0])

    # remember to flip x,y
    xfp = opts.pos[0] + ifu.y
    yfp = opts.pos[1] + ifu.x

    ra, dec = tp.xy2raDec(xfp, yfp)

    print("{:9.6f} {:9.6f}".format(float64(ra), float64(dec)))


def add_ra_dec(args=None):
    """Add ra, dec to detect, daophot catalogues and IFU cen files

    Parameters
    ----------
    args : list of strings, optional
        command line
    """
    parser = argparse.ArgumentParser(description="""Add ra and dec to a detect
                                     or daophot ALLSTAR catalogues or an ifucen
                                     file.""", parents=[astro_parent, ])
    parser.add_argument('files', nargs='+',
                        help="List of files to add ra, dec to")
    parser.add_argument('--fplane', default='fplane.txt',
                        help='Focal plane file')
    parser.add_argument('--fout', help='Filename to write to',
                        default='catalogue_out.fits')

    parser.add_argument('--dx', type=float, default=0.0,
                        help="Offset in arcseconds to apply "
                        " to x axis of IFU coordinates (additive)")

    parser.add_argument('--dy', type=float, default=0.0,
                        help="Offset in arcseconds to apply "
                        " to y axis of IFU coordinates (additive)")

    parser.add_argument('--ftype', default='line_detect', nargs=1, help='''Type
                        of input catalogue, to add ra and dec to. Options:
                        line_detect, cont_detect, daophot_allstar, ifucen''')

    # IHMP identification
    group_ihmp = parser.add_mutually_exclusive_group()
    group_ihmp.add_argument('--ihmps', nargs='+', help='List of IFU slots')
    group_ihmp.add_argument('--ihmp-regex', help='''Regex with 1 match group
                            corresponding to IFU slot''')

    opts = parser.parse_args(args)

    # Verify user input
    if not (opts.image or opts.astrometry):
        print("""Error: Either pass an image with TELRA, TELDEC, PARANGLE and
                 MJD in the header, or manually specify raccen, deccen and PA
                 with the astrometry option""")
        sys.exit(1)

    # Create IHMP/IFU slot list
    if opts.ihmps:
        ihmp_list = opts.ihmps
        if len(ihmp_list) != len(opts.files):
            msg = "Error: You passed {:d} files but {:d} IFU slots"
            print(msg.format(len(opts.files, opts.ihmp)))
            sys.exit(1)
    elif opts.ihmp_regex:
        # work out the IFU slot from the file name
        ihmp_list = []
        for fn in opts.files:

            try:
                match = re.search(opts.ihmp_regex, fn)
            except re.error:
                print("Error: Problem with the supplied ihmp-regex")
                raise

            if not match:
                msg = "Error: Regex found no matches for file {} with regex {}"
                print(msg.format(fn, opts.ihmp_regex))
                sys.exit(1)

            ihmp_list.append(match.group(1))
    else:
        print("""Error: Please specify IFU slots manually for each file with
                 --ihmp, or give a regex with which to extract the IFU slot
                 from the filename with ---regex-ihmp""")
        sys.exit(1)

    fplane = FPlane(opts.fplane)
    tp = ihmp_astrometry(opts)

    if 'line_detect' in opts.ftype:
        read_func = rc.read_line_detect
    elif 'cont_detect' in opts.ftype:
        read_func = rc.read_cont_detect
    elif 'daophot_allstar' in opts.ftype:
        read_func = rc.read_daophot
    elif 'ifucen' in opts.ftype:
        read_func = rc.read_ifu_cen_wrapper
    else:
        print("Error: unrecognised ftype option. Please choose line_detect,"
              " cont_detect or daophot_allstar")
        sys.exit(1)

    # Loop over the files, adding ra, dec
    tables = []
    for fn, ihmp in zip(opts.files, ihmp_list):
        x, y, table = read_func(fn)

        # skip empty tables
        if len(x) < 1:
            continue

        ifu = fplane.by_ifuslot(ihmp)

        # remember to flip x,y
        xfp = x + ifu.y + opts.dx
        yfp = y + ifu.x + opts.dy

        ra, dec = tp.xy2raDec(xfp, yfp)

        table['ra'] = ra
        table['dec'] = dec
        table['ifuslot'] = ihmp
        table['xfplane'] = xfp
        table['yfplane'] = yfp

        tables.append(table)

    if len(tables) < 1:
        print("Error: No entries in catalogue(s)")
        sys.exit(1)

    # output the combined table
    table_out = vstack(tables)

    print("Writing output to {:s}".format(opts.fout))

    # annoyingly have to specify comment variable for the write method for csv
    # output, but such a variable breaks the fits output!
    extn = op.splitext(opts.fout)[1]
    if extn == '.csv':
        table_out.write(opts.fout, comment='#')
    elif extn == '.txt':
        table_out.write(opts.fout, format='ascii')
    else:
        table_out.write(opts.fout)


def add_wcs(args=None):
    """Add WCS to fits file

    Parameters
    ----------
    args : list of strings, optional
        command line
    """
    parser = argparse.ArgumentParser(description="""Add WCS header to a fits
                                     file.""", parents=[astro_parent, ])
    parser.add_argument('file', help="Fits file to add WCS to")
    parser.add_argument('ihmp',  help='The IFU slot of the image')
    parser.add_argument('--fplane', default='fplane.txt',
                        help='Focal plane file')

    group_out = parser.add_mutually_exclusive_group()
    group_out.add_argument('--fout', help='Name of output file', default=None)
    group_out.add_argument('--pre', help='Prefix to append to output',
                           default='wcs.')

    # astrometry options
    parser.add_argument('--imscale', default=1.0,
                        help='Number of arcseconds per pixel')

    opts = parser.parse_args(args)

    # Verify user input
    if not (opts.image or opts.astrometry):
        print("""Error: Either pass an image with TELRA, TELDEC, PARANGLE and
                 MJD in the header, or manually specify raccen, deccen and PA
                 with the astro option""")
        sys.exit(1)

    # work out the name of the output file
    if opts.fout:
        fout = opts.fout
    else:
        path, name = op.split(opts.file)
        fout = op.join(path, opts.pre + name)

    # set up astrometry
    fplane = FPlane(opts.fplane)
    tp = ihmp_astrometry(opts, xscale=opts.imscale, yscale=opts.imscale)

    # get x, y offset of IFU in pixels
    ifu = fplane.by_ifuslot(opts.ihmp)
    x = -(ifu.x - 24.5)/(tp.wcs.wcs.cdelt[0]*3600.0)
    y = -(ifu.y - 24.5)/(tp.wcs.wcs.cdelt[1]*3600.0)

    # modify the tangent plane projection to be suitable for this IFU
    tp.wcs.wcs.crpix = [x, y]

    # open the image and write it out with the new header
    data, header = getdata(opts.file, header=True)
    header.extend(cards=tp.wcs.to_header())
    hdu = PrimaryHDU(data, header)
    hdu.writeto(fout)
