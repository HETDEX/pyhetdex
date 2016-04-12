RGB Image Creator
*****************

Instructions
============

After installing ``pyhetdex`` you can create a RGB colour image from a data cube
using ``datacube2rgb``. The default is to split the cube into three
equal-sized colour bins. You might also try: 4631,4731 A (dunno), 4815,4905 A
(Hbeta), 4967,5057 A (OII). The list of inputs is::

    positional arguments:
      fin                   filename of datacube
      fout                  output filename
    
    optional arguments:
      -h, --help            show this help message and exit
      --vmin VMIN           Minimum range for image stretch
      --vmax VMAX           Maximum range for image stretch
      --axes_off            Whether or not to display axes
      --red-filter RED_FILTER RED_FILTER
                            Range for red filter (A)
      --green-filter GREEN_FILTER GREEN_FILTER
                            Range for green filter (A)
      --blue-filter BLUE_FILTER BLUE_FILTER
                        Range for blue filter (A)


Example input::

    datacube2rgb  CuFeobject_dither0_dwarfGal.fits test2.eps --red-filter 
                  4967 5057 --green-filter 4815 4905 --blue-filter 4631 4731 --vmin 0 --vmax 1e5

.. warning::

    The WCS is currently hard-coded, nothing is used from the datacube header. 
   

