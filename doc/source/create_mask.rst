Mask Tools
==========

:mod:`pyhetdex.tools.create_mask` provides tools to create
masks of HETDEX data.

One of these tools is the ``generate_hetdex_mask`` executable.

Generate a mask for HETDEX data
-------------------------------

The command should run on command line if your installation of pyhetdex
was successful. The usage instructions are::

    usage: generate_hetdex_mask [-h] shot_file out_file rot_offset
    
    Generate a polygon file suitable for use in the Mangle mask software in
    vertices format. A line contains the four corners of an IFU in ra, dec. You
    can pass this to suitable Mangle commands, like poly2poly, with -iv4d input-
    type flag.
    
    positional arguments:
      shot_file   An ascii file containing the header'SHOTID RACEN DECCEN PARANGLE
                  FPLANE' and appropriate entries. Coordinates should be given in
                  degrees.
      out_file    File name for the Mangle compatible polygon file
      rot_offset  Rotation difference to add to PARANGLE
    
    optional arguments:
      -h, --help  show this help message and exit

The shot file should contain the ra, dec and rotation of the focal plane, and
should be an ascii file with this format, and exactly this header::
 
    SHOTID RACEN      DECCEN    PARANGLE   FPLANE
    00000 167.813861 46.058700 78.468042 fplane.txt
    00001 169.095867 46.394200 77.905286 fplane.txt
    00002 171.701864 47.020500 76.839713 fplane.txt
    00003 168.022346 46.994700 76.884009 fplane.txt
    00004 167.069869 49.244000 72.877809 fplane.txt
    00005 167.013876 49.966300 71.520487 fplane.txt
    00006 169.972862 48.214300 74.749727 fplane.txt
    00007 165.321877 50.105400 71.256308 fplane.txt
    00008 170.497867 50.080200 71.304517 fplane.txt

The parameter `SHOTID` can be any number or string. `FPLANE` should be the full file path
to the fplane file and the coordinates should be in degrees.

The output file gives the corners of each IFU and can be used as an input
to the Mangle set of tools `<http://space.mit.edu/~molly/mangle/>`_ See the Mangle
documentation for the steps required for speeding up  this mask or converting
it to other Mangle formats. 
