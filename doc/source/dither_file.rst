Dither file creator
*******************

Instructions
============

After installing ``pyhetdex`` you can create a dither file for an IFU on command
line via the ``dither_file`` executable. The full list of arguments and options
is::


    usage: dither_file [-h] [-o OUTFILE] [-m MODELBASES [MODELBASES ...]]
                    [-t {ifuid,ifuslot,specid}] [-s SHOTDIR] [-O ORDER_BY]
                    [-e EXTENSION] [-d DITHERPOS [DITHERPOS ...] | -f
                    DITHERPOS_FILE]
                    id fplane basenames [basenames ...]

    Produce a dither file for the give id.

    positional arguments:
    id                    id of the chosen IFU
    fplane                The fplane file
    basenames             Basename(s) of the data files. The ``{dither}`` and
                          ``{id}`` placeholders are replaced by the dither
                          number and the provided id. E.g., if the ``id``
                          argument is ``001``, the string
                          ``file_D{dither}_{id}`` is replaced, for the first
                          dither, by file_D1_001. The placeholders don't have to
                          be present. The number of files must be either one or
                          as many as the number of dithers in the ``ditherpos``
                          file.

    optional arguments:
    -h, --help             show this help message and exit
    -o OUTFILE, --outfile OUTFILE
                            Name of a file to output. It accepts the same
                            placeholders as ``basename``, but ``{dither}`` is the
                            number of dithers (default: dither_{id}.txt)
    -m MODELBASES [MODELBASES ...], --modelbases MODELBASES [MODELBASES ...]
                            Basename(s) of the model files. It accepts that same
                            place holders as ``basename``. The number of files
                            must be either one or as many as the number of dithers
                            in the ``ditherpos`` file. (default:
                            ['masterflat_{id}'])
    -t {ifuid,ifuslot,specid}, --id-type {ifuid,ifuslot,specid}
                            Type of the id (default: ifuslot)
    -s SHOTDIR, --shotdir SHOTDIR
                            Directory of the shot. If not provided use some
                            sensible default value for image quality and
                            normalisation. WARNING: at the moment not used
                            (default: None)
    -O ORDER_BY, --order-by ORDER_BY
                            If given, order the ``basenames`` files by the value
                            of the header keyword 'order_by' (default: None)
    --use-hetpupil          Use $CUREBIN/hetpupil to get the relative illumination
                            from the files passed via basename. The ``extension``
                            is used to have valid file names. (default: False)
    -e EXTENSION, --extension EXTENSION
                            Extension appended to the base names to create valid
                            file names (default: _L.fits)
    -d DITHERPOS [DITHERPOS ...], --ditherpos DITHERPOS [DITHERPOS ...]
                            Dither postions (default: [0.0, -1.27, -1.27, 0.0,
                            0.73, -0.73])
    -f DITHERPOS_FILE, --ditherpos-file DITHERPOS_FILE
                            Name of the file containing the dither shifts. The
                            expected format is ``id x1 x2 ... xn y1 y2 ... yn``.
                            Normally the ``id`` is ``ifuslot``. This option
                            deactivate the ``ditherpos`` one (default: None)

Running::

    dither_file -f vhc_config/reference_files/dither_positions.txt\
        067 fplane.txt HETDEX_obs-1_D{dither}_{id}

creates a file called ``dither_067.txt``::

    # basename          modelbase           ditherx dithery                seeing norm airmass
    HETDEX_obs-1_D1_067 masterflat_067 0.000000 0.000000 1.600 1.0000 1.2200
    HETDEX_obs-1_D2_067 masterflat_067 0.615000 1.065000 1.600 1.0000 1.2200
    HETDEX_obs-1_D3_067 masterflat_067 1.230000 0.000000 1.600 1.0000 1.2200

The following::

    dither_file -m model-1_{id}_D{dither}\
        -o dither_067.txt 067 fplane.txt\
        HETDEX_obs-1_{id}_D{dither}

creates the following file::

    # basename          modelbase           ditherx dithery                seeing norm airmass
    HETDEX_obs-1_067_D1 model-1_067_D1 0.000000 0.000000 1.600 1.0000 1.2200
    HETDEX_obs-1_067_D2 model-1_067_D2 -1.27000 0.730000 1.600 1.0000 1.2200
    HETDEX_obs-1_067_D3 model-1_067_D3 -1.27000 0.730000 1.600 1.0000 1.2200

If the dither number is not in the base names but is stored in a header
keyword, it is possible to pass the list of base names to ``dither_file`` and
tell it to sort the names. To do so, you also give the name of the header
keyword containing the dither number and, if different from the default, the
extension to append to the base names to form valid file names. So, assuming
that dithers are taken sequentially, the following::

    dither_file -O DITHER\
        -f vhc_config/trunk/reference_files/dither_positions.txt\
        067 fplane.txt\
        20160410T000030_067_sci 20160410T000003_067_sci\
        20160410T000017_067_sci

writes the file::

    # basename          modelbase           ditherx dithery                seeing norm airmass
    20160410T000003_067_sci masterflat_067 0.000000 0.000000 1.600 1.0000 1.2200
    20160410T000017_067_sci masterflat_067 0.615000 1.065000 1.600 1.0000 1.2200
    20160410T000030_067_sci masterflat_067 1.230000 0.000000 1.600 1.0000 1.2200

With the ``--use-hetpupil`` switch, the default illumination model, is replaced
with one that uses the ``hetpupil`` executable from cure to estimate
the average pupil illumination and thus the normalisation. If, e.g., for the
above three files ``hetpupil`` return 0.9, 1.2 and 0.7, running::

    dither_file -O DITHER --use-hetpupil\
        -f vhc_config/trunk/reference_files/dither_positions.txt\
        067 fplane.txt\
        20160410T000030_067_sci 20160410T000003_067_sci\
        20160410T000017_067_sci

will create a file with the second to last column like in the following example::

    # basename          modelbase           ditherx dithery                seeing norm airmass
    20160410T000003_067_sci masterflat_067 0.000000 0.000000 1.600 1.0000 1.2200
    20160410T000017_067_sci masterflat_067 0.615000 1.065000 1.600 1.3333 1.2200
    20160410T000030_067_sci masterflat_067 1.230000 0.000000 1.600 0.7778 1.2200

The output of ``hetpupil`` is normalized to the value of the first file.
