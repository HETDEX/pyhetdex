Dither file creator
*******************

Instructions
============

After installing ``pyhetdex`` you can create a dither file for an IFU on command
line via the ``dither_file`` executable. The full list of arguments and options
is::

    usage: dither_file [-h] [-m MODELBASE] [-t {ifuid,ihmpid,specid}] [-s SHOTDIR]
                    outfile id fplane ditherpos basename

    Produce a dither file for the give id.

    positional arguments:
    outfile               Name of a file to output
    id                    id of the chosen IFU
    fplane                The fplane file
    ditherpos             Name of the file containing the dither shifts. The
                            expected format is ``id x1 x2 ... xn y1 y2 ... yn``.
                            Normally the ``id`` is ``ihmpid``
    basename              Basename of the data files. The ``{dither}`` and
                            ``{id}`` placeholders are replaced by the dither
                            number and the provided id. E.g., if the ``id``
                            argument is ``001``, the string
                            ``file_D{dither}_{id}`` is replaced, for the first
                            dither, by file_D1_001. The placeholders don't have to
                            be present.

    optional arguments:
    -h, --help            show this help message and exit
    -m MODELBASE, --modelbase MODELBASE
                            Basename of the model files. It accepts that same
                            place holders as ``basename`` (default:
                            masterflat_{id})
    -t {ifuid,ihmpid,specid}, --id-type {ifuid,ihmpid,specid}
                            Type of the id (default: ihmpid)
    -s SHOTDIR, --shotdir SHOTDIR
                            Directory of the shot. If not provided use some
                            sensible default value for image quality and
                            normalisation (default: None)

Running::

    dither_file dither_067.txt 067 fplane.txt\
        vhc_config/trunk/reference_files/dither_positions.txt\
        HETDEX_obs-1_D{dither}_{id}

creates a file called ``dither_067.txt``::

    # basename          modelbase           ditherx dithery                seeing norm airmass
    HETDEX_obs-1_D1_067 masterflat_067 0.000000 0.000000 1.600 1.0000 1.2200
    HETDEX_obs-1_D2_067 masterflat_067 0.615000 1.065000 1.600 1.0000 1.2200
    HETDEX_obs-1_D3_067 masterflat_067 1.230000 0.000000 1.600 1.0000 1.2200

The following::

    dither_file -m model-1_{id}_D{dither}\
        dither_067.txt 067 fplane.txt\
        vhc_config/trunk/reference_files/dither_positions.txt\
        HETDEX_obs-1_{id}_D{dither}

creates the following file::

    # basename          modelbase           ditherx dithery                seeing norm airmass
    HETDEX_obs-1_067_D1 model-1_067_D1 0.000000 0.000000 1.600 1.0000 1.2200
    HETDEX_obs-1_067_D2 model-1_067_D2 0.615000 1.065000 1.600 1.0000 1.2200
    HETDEX_obs-1_067_D3 model-1_067_D3 1.230000 0.000000 1.600 1.0000 1.2200

Seeing and normalisation values are taken from the image quality
(:mod:`pyhetdex.het.image_quality`) and illumination servers
(:mod:`pyhetdex.het.illumination`), based on the guide probe information in the
shot directory. 

.. warning::
    Currently the servers just return fixed values, they still need to be
    implemented.
