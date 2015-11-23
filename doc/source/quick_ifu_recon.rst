Quick IFU reconstruction
========================

:mod:`pyhetdex.het.reconstruct_ifu` provides ways to reconstructs an IFU image
from fiber extract frames
(:class:`~pyhetdex.het.reconstruct_ifu.ReconstructedIFU`) or fits images
(:class:`~pyhetdex.het.reconstruct_ifu.QuickReconstructedIFU`).

The latter is exposed via the ``reconstructIFU`` executable.

Instructions
------------

::

    usage: reconstructIFU [-h] [-o OUTFILE] [-l LDIST] [-r RDIST] [-s SCALE]
                        ifucen files [files ...]

    Reconstruct the IFU image from a list of fits images.

    positional arguments:
    ifucen                Name of the IFUcen file
    files                 The input images

    optional arguments:
    -h, --help            show this help message and exit
    -o OUTFILE, --outfile OUTFILE
                            Name of a file to output (default: reconstruct.fits)
    -l LDIST, --ldist LDIST
                            Name of the distortion file for the left spectrograph;
                            at least one of 'ldist' or 'rdist' must be provided
                            (default: None)
    -r RDIST, --rdist RDIST
                            Name of the distortion file for the right spectrograph
                            (default: None)
    -s SCALE, --scale SCALE
                            Scale of the pixels in the reconstructed image
                            (default: 0.3)

For each of the output file the following steps are performed:

1) if present the ``BIASSEC`` is extracted and subtracted from the data;
2) the dither number, channel and amplifier are extracted from the header;
3) using the channel and amplifier information and the information for the
   correct distortion files, ``ldist`` and ``rdist`` some of the flux from each
   fiber;
4) using the IFUcen file, the flux from each fiber is associated to the
   corresponding x/y position of the fiber head;
5) after all the files has being exhausted, the flux from the dithers is added
   and the final image saved to ``outfile``.
