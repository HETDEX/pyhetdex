#Description of the files
All the files needed for the tests are in this directory (`tests/data`). This is
a description of the files for future reference

## Sky background subtraction tests
The following three files are used to test the sky background subtraction from
fiber extracted frames:

    1. Fejpes20120301T000000_046L_sci.fits
    2. FeSjpes20120301T000000_046L_sci.fits
    3. FeSkyjpes20120301T000000_046L_sci.fits

They are, in order:

1. the fiber extracted frame to which apply the sky background subtraction 
2. reference fiber extracted sky subtracted frames: the frame is created using
`cure` tool `subtractsky`
3. reference fiber extracted sky frames: the frame is created using `cure` tool
`subtractsky`

## IFU reconstruction

The following files are used to test the IFU reconstruction and image quality
estimation.

Fiber extracted frames:

    fast_SIMDEX-4000-obs-1_D1_046_L.fits
    fast_SIMDEX-4000-obs-1_D1_046_R.fits
    fast_SIMDEX-4000-obs-1_D2_046_L.fits
    fast_SIMDEX-4000-obs-1_D2_046_R.fits
    fast_SIMDEX-4000-obs-1_D3_046_L.fits
    fast_SIMDEX-4000-obs-1_D3_046_R.fits

Dither file containing the exact description, without the `fast` part of the
name and with different base names. There are three dither files to test the
different ways to reconstruction the image

    dither_fast_SIMDEX-4000-obs-1_046.txt
    dither_SIMDEX-4000-obs-1_046.txt
    dither other_SIMDEX-4000-obs-1_046.txt

File with the position of the fibers in the IFU head. The second one is for
testing commented lines, lines with non numerical fiber number (both mean
broken fibers) and with an alive fiber with 0 throughput (It fails as the fiber
should be alive but there is no throughput)

    IFUcen_HETDEX.txt
    IFUcen_HETDEX_fail.txt
