Dither file creator
*******************

Instructions
============

After installing ``pyhetdex`` you can create a dither file for
an IFU on command line via ::

  dither_file [-h] [--shotdir SHOTDIR] outfile ifuid fplane ditherpos basename modelbase


The positional arguments are:
 -  outfile:            Name of a file to output
 -  ifuid:              id of the chosen IFU
 -  fplane:             The fplane file
 -  ditherpos:          List of dither positions per ifu
 -  basename:           Basename of the data files
 -  modelbase:          Basename of the model files

The optional arguments are:
  - "-h, --help":         show this help message and exit
  - "--shotdir SHOTDIR":  Directory of the shot (defaults to current dir)

For the dithers the dither number and IFU id are appended to the basename and modelbase, e.g. for IFU 067 "D1_067", 
"D2_067" and "D3_067" are appended. For more flexibility you can use the Python class directly. Normalisation and 
seeing values are taken from the image quality and illumination servers, based on the guide probe information in the 
shot directory. **Currently the servers just return fixed values, they still need to be implemented.** 

Example
=======

You can try running this using data in the test directory ::

  dither_file dither_067.txt 067 tests/data/fplane.txt tests/data/dither_positions.txt test test



