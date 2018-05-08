# Misc python library to support HETDEX software and data analysis
# Copyright (C) 2018  "The HETDEX collaboration"
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
from pyhetdex.tools.files import file_tools as ft
from astropy.io import fits
import hashlib


def check_repeat(dirs, write_key=False, verbose=False):

    try:
        from awise.common.log.Message import Message
    except ImportError:
        def Message(s):
            if verbose:
                print(s)

    for dirname in dirs:

        Message('Checking repeat data on %s' % dirname)
        files = list(ft.scan_files(dirname, matches='*virus*.fits',
                                   recursive=True))

        ifuslots = set([f.split('_')[-2] for f in files])

        for ifuslot in ifuslots:
            Message('Checking ifuslot %s ' % ifuslot)
            files = list(ft.scan_files(dirname, matches='*virus*_%s_*.fits' %
                                       ifuslot, recursive=True))

            hdulist = []
            hashlist = []

            for f in files:
                hdu = fits.open(f, mode='update')
                hdulist.append(hdu)
                hashlist.append(hashlib.md5(hdu[0].data).hexdigest())

                for i in range(0, len(hdulist)):
                    for j in range(i+1, len(hdulist)):
                        if hashlist[i] == hashlist[j]:
                            Message('%s and %s are the same' %
                                    (hdulist[i].filename(),
                                     hdulist[j].filename()))
                            if 'REPEAT' in hdulist[i][0].header:
                                if not hdulist[i][0].header['REPEAT']:
                                    Message('%s is repeating, but REPEAT'
                                            ' keyword is false'
                                            % hdulist[i].filename())
                            if write_key:
                                hdulist[i][0].header['REPEAT'] = True
                                hdulist[j][0].header['REPEAT'] = True

            for h in hdulist:
                h.close()


def argument_parser(argv=None):
    """Parse the command line"""
    import argparse as ap

    # Parse user input
    description = """Check virus images for repeated data due to a
                     controller problem."""

    p = ap.ArgumentParser(description=description,
                          formatter_class=ap.ArgumentDefaultsHelpFormatter)

    p.add_argument('dirs', nargs='+',
                   help="""The input night directories""")

    p.add_argument('-k', '--write_key', help="""Write the REPEAT header keyword
                   to the files found""", action='store_true')
    p.add_argument('-v', '--verbose', help="""Print the names of the files detected
                   as duplicates""", action='store_true')

    return p.parse_args(argv)


def main(argv=None):

    args = argument_parser(argv=argv)

    check_repeat(args.dirs, write_key=args.write_key, verbose=args.verbose)


if __name__ == '__main__':
    main()
