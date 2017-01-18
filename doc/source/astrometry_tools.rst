Astrometry Tools
================

.. warning:: The astrometry output from these routines will
   only be as good as the estimate of the central ra and dec 
   of the shot, the measurement of the PA and the 
   accuracy of the focal plane and IFUcen files. At this
   stage the results will at best be only accurate to a few
   arcseconds.


:mod:`pyhetdex.coordinates.astrometry` provides tools to
add ra, dec columns to catalogues or WCS headers to FITS files.

One of these tools is called ``add_ra_dec`` executable.

Add ra and dec to a catalogue
-----------------------------

The command should run on command line if your installation of pyhetdex
was successful. The usage instructions are::

    usage: add_ra_dec [-h] [--fplane FPLANE] [--fout FOUT] [--ftype FTYPE]
                  [--astrometry ASTROMETRY ASTROMETRY ASTROMETRY | --image IMAGE]
                  [--ihmps IHMPS [IHMPS ...] | --ihmp-regex IHMP_REGEX]
                  files [files ...]

    Add ra and dec to a detect or daophot ALLSTAR catalogue.
    
    positional arguments:
      files                 List of files to add ra, dec to
    
    optional arguments:
      -h, --help            show this help message and exit
      --fplane FPLANE       Focal plane file
      --fout FOUT           Filename to write to
      --ftype FTYPE         Type of input catalogue, to add ra and dec to.
                            Options: line_detect, cont_detect, daophot_allstar
      --astrometry ASTROMETRY ASTROMETRY ASTROMETRY
                            RA DEC and PA of the focal plane center (degrees)
      --image IMAGE         An image, with a header to grab ra, dec and PA from
                            (DONT USE THIS)
      --ihmps IHMPS [IHMPS ...]
                            List of IFU slots
      --ihmp-regex IHMP_REGEX
                            Regex with 1 match group corresponding to IFU slot


You must pass some information about the telescope pointing. The ``--astrometry`` option
is the way to do this, with this option you need to pass the ra, dec and PA (all in degrees)
of the observation e.g. for the M3 commissioning run a good choice is::

    --astrometry 205.543395821 28.3792133418 257.654951

These numbers are the position of the center of the optical axis, for HETDEX survey
observations they'll be the positions in the schedule file. For other projects you'll
have to compute it from the acquisition camera or the guide probes. To work out where
a particular IFU is with respect to this position, a focal fplane file must also be
passed along with some information on the IFU slot of the images. To pass this
latter information you can either give a list of IFU slots (in the same order of the
input files) e.g.::

    --ihmps 074 056 023 

or pass a regular expression with which to extract the IFU slot from the file name e.g.::

    --ihmp-regex 'detect_(.*)_line.dat'

You can pass one or multiple of: line catalogues from detect, continuum catalogues from detect
or ALLSTAR catalogues from DAOPHOT. All files must be of the same type and the type must
be specified with the ``--ftype`` flag. The output can either be a FITS file or a CSV file,
choose the output type by adding either ``.fits`` or ``.csv`` to the end of the output
filename specified with ``--fout``. 

Here are some examples::

 
    add_ra_dec --fplane fplanetmp.txt \
               --astrometry 205.543395821 28.3792133418 257.654951 \
               --ftype daophot_allstar --fout cat.fits \
               --ihmp-regex '061706_(.*).als' 061706_*.als

or specifying the IFU slots manually::

    add_ra_dec --fplane fplanetmp.txt \ 
                --astrometry 205.543395821 28.3792133418 257.654951 \
               --ftype daophot_allstar --fout cat.csv \
               --ihmps 095 075 073 -- 061706_095.als 061706_075.als 061706_073.als

Note the double-dash ``--`` can be used to explicitly separate the arguments passed to the flags from the final input files. Here's
a final example with a different input file type::

    add_ra_dec --fplane fplanetmp.txt \
               --astrometry 205.543395821 28.3792133418 257.654951 --ftype line_detect \
               --fout cat.fits --ihmp-regex 'detect_(.*)_.*_line.dat' \
               detect_084_20160512T055309.7_line.dat detect_074_20160512T055309.7_line.dat


Convert between x, y on IFU to ra, dec on command line
------------------------------------------------------

The command line tool ``xy_to_ra_dec`` accepts astrometry info (using the ``--astrometry`` option in the same way as 
in ``add_ra_dec``), reads in a position - with respect to the center of the IFU - and prints
the ra, dec to standard output. Note positions from ds9 or daophot might be with respect the the bottom 
left of the IFU, not necessarily the center of the IFU or its position as defined in the fplane file.

Here is the help info::

    usage: xy_to_ra_dec [-h] [--fplane FPLANE]
                    [--astrometry ASTROMETRY ASTROMETRY ASTROMETRY | --image IMAGE]
                    [--ihmp IHMP]
                    pos pos

    Convert between in-IFU x, y and on-sky ra, dec.
    
    positional arguments:
      pos                   Position in IFU (w.r.t. to IFU position in fplane
                            file, i.e. the IFU center)
    
    optional arguments:
      -h, --help            show this help message and exit
      --fplane FPLANE       Focal plane file
      --astrometry ASTROMETRY ASTROMETRY ASTROMETRY
                            RA DEC and PA of the focal plane center (degrees)
      --image IMAGE         An image, with a header to grab ra, dec and PA from
                            (DONT USE THIS)
      --ihmp IHMP           IFU slot of desired IFU
 


Here is an example::

    xy_to_ra_dec --fplane fplane.txt --astrometry 205.547 28.376 254.6  --ihmp 073  20.969 -23.712



Add WCS to a fits image
-----------------------

.. warning:: For some reason the x and y coordinates are a flipped in
   the WCS. So this doesn't actually work yet...

The routine ``add_wcs`` adds a (2D) WCS header to fits images and datacubes from 
VIRUS. The usage is::

    usage: add_wcs [-h] [--fplane FPLANE] [--fout FOUT | --pre PRE]
               [--imscale IMSCALE]
               [--astrometry ASTROMETRY ASTROMETRY ASTROMETRY | --image IMAGE]
               file ihmp

    Add WCS header to a fits file.
    
    positional arguments:
      file                  Fits file to add WCS to
      ihmp                  The IFU slot of the image
    
    optional arguments:
      -h, --help            show this help message and exit
      --fplane FPLANE       Focal plane file
      --fout FOUT           Name of output file
      --pre PRE             Prefix to append to output
      --imscale IMSCALE     Number of arcseconds per pixel
      --astrometry ASTROMETRY ASTROMETRY ASTROMETRY
                            RA DEC and PA of the focal plane center (degrees)
      --image IMAGE         An image, with a header to grab ra, dec and PA from
                            (DONT USE THIS)


The ``--fplane`` and ``--astrometry`` parameters are explained above. The inserted
fits header assumes position 24.5 arcsecs, 24.5 arcsecs is the center of your image. It also
assumes no transformations or rotations have been applied to the raw data. Here is an
example::

    add_wcs --fplane fplanetmp.txt --astrometry 205.543395821 28.3792133418 257.654951 CuFepses20160604T063029.1_085_sci.fits 085
