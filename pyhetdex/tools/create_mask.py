""" Create Mask module

Module to produce masks for HETDEX 


.. moduleauthor:: Daniel Farrow <dfarrow@mep.mpg.de>
"""
 

from __future__ import (absolute_import, print_function)
import argparse
from six import iteritems
from astropy.table import Table, vstack
from pyhetdex.het.fplane import FPlane
from pyhetdex.coordinates.tangent_projection import TangentPlane


def generate_ifu_corner_ra_decs(tp, fplane):
    """
    Generate the ra, dec of the four corners of each 
    for a shot. Does this by evaluating the
    ra and dec at a number of points around each IFU.

    Parameters
    ----------
    tp : pyhetdex.coordinates.tangent_projection:TangentPlane
        the astrometry of the shot
    fplane : pyhetdex.het.fplane:FPlane
        the focal plane object

    Returns
    -------
    ifuslots : list
        a list of the IFU slots
    table  : astropy.table:Table
        table with the corners of the IFU in ra and dec and the IFUSLOT
    """

    xlim = 25.0
    ylim = 25.0
    corners = [[xlim, ylim], [xlim, -1.0*ylim], [-1.0*xlim, -1.0*ylim], [-1.0*xlim, ylim]] 
    table = Table(names=['ra1', 'dec1', 'ra2', 'dec2', 'ra3', 'dec3', 'ra4', 'dec4', 'ifuslot', 'shotid'],
                  dtype=['f', 'f', 'f', 'f', 'f', 'f', 'f', 'f', 'S3', 'S15'])

    for ifuslot, ifu in iteritems(fplane.difus_ifuslot):
        ras = []
        decs = []

        for x, y in corners: 
          
            # remember to flip x,y
            xfp = x + ifu.y
            yfp = y + ifu.x
 
            ra, dec = tp.xy2raDec(xfp, yfp)

            ras.append(ra)
            decs.append(dec)

        table.add_row([ras[0], decs[0], ras[1], decs[1], 
                       ras[2], decs[2], ras[3], decs[3], ifuslot, '-9999999'])
       

    return table 


def generate_mangle_polyfile(args=None):
    """
    Generate a Mangle polygon file in vertices format

    Mangle reference: http://space.mit.edu/~molly/mangle/

    """
  
    parser = argparse.ArgumentParser(description="Generate a polygon file suitable for use"
                                     " in the Mangle mask software in vertices format. A line"
                                     " contains the four corners of an IFU in ra, dec."
                                     " You can pass this to suitable Mangle commands,"
                                     " like poly2poly, with -iv4d input-type flag.")

    parser.add_argument("shot_file", help="An ascii file containing the header"
                                          "'SHOTID RACEN DECCEN PARANGLE FPLANE' and appropriate"
                                          " entries. Coordinates should be given in degrees.")

    parser.add_argument("out_file", help="File name for the Mangle compatible polygon file")

    parser.add_argument("rot_offset", help="Rotation difference to add to PARANGLE", default=0.0, type=float)

    opts = parser.parse_args()

    tables = []

    try:
        table_shots = Table.read(opts.shot_file, format='ascii')
    except IOError as e: 
        print("Problem opening input file {:s}".format(opts.shot_file))
        raise e

    fplane_name_last = ""
    for row in table_shots:

        if row['FPLANE'] != fplane_name_last or not fplane:
            fplane = FPlane(row['FPLANE']) 
            fplane_name_last = row['FPLANE']

        # Carry out required changes to astrometry
        rot = 360.0 - (row['PARANGLE'] + 90.0 + opts.rot_offset)
        tp = TangentPlane(row['RACEN'], row['DECCEN'], rot)

        table = generate_ifu_corner_ra_decs(tp, fplane)
        print(row['SHOTID'])
        table['shotid'] = row['SHOTID']
        tables.append(table)

    table_out = vstack(tables)
    table_out.write(opts.out_file, format='ascii.commented_header', comment='#')












 



























