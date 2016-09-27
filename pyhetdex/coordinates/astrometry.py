""" Astrometry module

Module to add astrometry to HETDEX catalgoues and images


.. moduleauthor:: Daniel Farrow <dfarrow@mep.mpg.de>
"""
   
from __future__ import (absolute_import, print_function)
import re
import os.path as op
import glob
import sys
import argparse
import astropy.units as units
from numpy import cos, sin, deg2rad, rad2deg
from astropy.io.fits import getheader, getdata, PrimaryHDU
from astropy.table import Table, vstack, hstack
from astropy.coordinates import SkyCoord, FK5
from pyhetdex.tools.read_catalogues import *
from pyhetdex.het.fplane import FPlane
from pyhetdex.coordinates.tangent_projection_astropy import TangentPlane
from pyhetdex.coordinates.transformations import hms2decimal, dms2decimal

def ihmp_astrometry(opts, xscale=1.0, yscale=1.0):
    """
    Set up a tangent plane projection from
    parsed command line arguments from ArgParse

    Parameters
    ----------
    opts : 
        command line options, either 'image' for a fits
        file with TELRA, TELDEC, PARANGLE, MJD or and
        'astrometry' option to manually specify coordinates 
    xscale, yscale :
        number of arcseconds per pixel for the WCS
        header created (default 1,1)

    Returns
    -------
    tp : pyhetdex.coordinates.tangent_projection_astropy.TangentPlane
        tangent plane object to use for astrometry
    """
   
    if opts.image:
        raise Exception("Don't use this option, the header values aren't accurate enough")
        # Set up astrometry using the values in the header
        print("Reading header values from {:s}".format(opts.image))
        head = getheader(opts.image)
        rastr = head['TELRA']
        decstr = head['TELDEC']
        pa = head['PARANGLE'] + 1.6 # empirical offset between PARANGLE and rotation

        # convert from local equinox to J2000
        equinox = 2016 + (head['MJD'] - 57388)/365.24
        ra_local_eqx =  hms2decimal(rastr)
        dec_local_eqx = dms2decimal(decstr)
        gc = SkyCoord(ra_local_eqx*units.degree, dec_local_eqx*units.degree,
                      frame='fk5', equinox='J{:0.4f}'.format(equinox))
        s = gc.transform_to(FK5(equinox='J2000.0'))

        # From Majo (with a bit of tweaking)
        TELRA = 0.002414529 #0.0018589733 
        TELDEC = -0.00307875  #-0.0033565244

        print(s.ra.deg + TELRA, s.dec.deg + TELDEC, pa)
        tp = TangentPlane(s.ra.deg + TELRA, s.dec.deg + TELDEC, pa, x_scale=xscale, y_scale=yscale)
    else:
        # Carry out required changes to astrometry
        rot = 360.0 - (opts.astrometry[2] + 90. + 1.8)

        # Set up astrometry from user supplied options
        tp = TangentPlane(opts.astrometry[0], opts.astrometry[1], rot)

    return tp
 
def add_ra_dec(args=None):
    """

    Add ra, dec to detect and daophot catalogues

    """   

    parser = argparse.ArgumentParser(description="Add ra and dec to a detect or daophot ALLSTAR catalogue.")
    parser.add_argument('files', nargs='+', help="List of files to add ra, dec to")
    parser.add_argument('--fplane', default='fplane.txt', help='Focal plane file')
    parser.add_argument('--fout', help='Filename to write to', default='catalogue_out.fits')

    parser.add_argument('--ftype', default='line_detect', nargs=1, help='''Type of input catalogue, to add ra and dec to. 
                                                                Options: line_detect, cont_detect, daophot_allstar''')
 
    # astrometry options
    group_astro = parser.add_mutually_exclusive_group()
    group_astro.add_argument('--astrometry', nargs=3, type=float, help='RA DEC and PA of the focal plane center (degrees)')
    group_astro.add_argument('--image', help='An image, with a header to grab ra, dec and PA from (DONT USE THIS)')

    # IHMP identification
    group_ihmp = parser.add_mutually_exclusive_group()
    group_ihmp.add_argument('--ihmps', nargs='+', help='List of IFU slots')
    group_ihmp.add_argument('--ihmp-regex', help='Regex with 1 match group corresponding to IFU slot')

    opts = parser.parse_args(args)

    # Verify user input
    if not (opts.image or opts.astrometry):
        print("""Error: Either pass an image with TELRA, TELDEC, PARANGLE and MJD in the header, 
                 or manually specify raccen, deccen and PA with the astro option""") 
        sys.exit(1)

    # Create IHMP/IFU slot list
    if opts.ihmps: 
        ihmp_list = opts.ihmps
        if len(ihmp_list) != len(opts.files):
            print("Error: You passed {:d} files but {:d} IFU slots".format(len(opts.files, opts.ihmp)))
            sys.exit(1)
    elif opts.ihmp_regex:
       # work out the IFU slot from the file name
       ihmp_list = []
       for fn in opts.files:

           try:
               match = re.search(opts.ihmp_regex, fn)
           except:
               print("Error: Problem with the supplied ihmp-regex")
               raise 

           if not match:
               print("Error: Regex found no matches for file {:s} with regex {:s}".format(fn, opts.ihmp_regex))
               sys.exit(1)

           ihmp_list.append(match.group(1))
    else:
        print("""Error: Please specify IFU slots manually for each file with --ihmp, or
                give a regex with which to extract the IFU slot from the filename with
                ---regex-ihmp""")               
        sys.exit(1)
   

    fplane = FPlane(opts.fplane)
    tp = ihmp_astrometry(opts) 
     
    if 'line_detect' in opts.ftype:
        read_func = read_line_detect
    elif 'cont_detect' in opts.ftype:
        read_func = read_cont_detect
    elif 'daophot_allstar' in opts.ftype: 
        read_func = read_daophot
    else: 
        print("Error: unrecognised ftype option. Please choose line_detect, cont_detect or daophot_allstar")
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
        xfp = x + ifu.y
        yfp = y + ifu.x
 
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

    # annoyingly have to specify comment variable for 
    # the write method for csv output, but such a 
    # variable breaks the fits output!
    extn = op.splitext(opts.fout)[1]
    if extn == '.fits':
        table_out.write(opts.fout)
    elif extn == '.txt':
        table_out.write(opts.fout, format='ascii')
    else:
        table_out.write(opts.fout, comment='#')


def add_wcs(args=None):
    """

    Add WCS to fits file

    """   

    parser = argparse.ArgumentParser(description="Add WCS header to a fits file.")
    parser.add_argument('file', help="Fits file to add WCS to")
    parser.add_argument('ihmp',  help='The IFU slot of the image')
    parser.add_argument('--fplane', default='fplane.txt', help='Focal plane file')


    group_out = parser.add_mutually_exclusive_group()
    group_out.add_argument('--fout', help='Name of output file', default=None)
    group_out.add_argument('--pre', help='Prefix to append to output', default='wcs.')
 
    # astrometry options
    parser.add_argument('--imscale', default=1.0, help='Number of arcseconds per pixel')
    group_astro = parser.add_mutually_exclusive_group()
    group_astro.add_argument('--astrometry', nargs=3, type=float, help='RA DEC and PA of the focal plane center (degrees)')
    group_astro.add_argument('--image', help='An image, with a header to grab ra, dec and PA from (DONT USE THIS)')

    opts = parser.parse_args(args)

    # Verify user input
    if not (opts.image or opts.astrometry):
        print("""Error: Either pass an image with TELRA, TELDEC, PARANGLE and MJD in the header, 
                 or manually specify raccen, deccen and PA with the astro option""") 
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






    










