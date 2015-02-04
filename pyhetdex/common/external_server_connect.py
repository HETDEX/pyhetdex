"""
Download a SDSS or DSS image and plot them.

Largely copied from ``hetdexshuffle/visualize.py`` with some minor
modifications

.. todo::
    Rename module: the module is not a generic connection to a server, but
    specific to fetching and plotting DSS and SDSS images.

    Improve the documentation

    ``ifu_centers``: :func:`~plotFocalPlaneQuicklook` and :func:`~get_image`
    have a ``ifu_centers`` arguments, which is the center of the IFUs in the
    focal plane. This is confusing as in HETDEX jargon IFUCen refers to the
    fibers **within** one IFU

    write tests
"""
from __future__ import absolute_import, print_function

import os
from StringIO import StringIO
import urllib

from PIL import Image
from PIL import ImageFilter

import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from matplotlib.collections import PatchCollection

from astropy.io import fits

import numpy as np

from pyhetdex.common import file_tools as ft


def deg2pix(degree, scale=1.698):
    """Convert degrees in pixels, given a pixel scale

    Parameters
    ----------
    degree: float
        angle to convert
    scale: float, optional
        pixel scale

    Returns
    -------
    float:
        number of pixels
    """
    return degree * 3600. / scale


def wcs2pix(ra, dec, ra0, dec0, scale=1.698, im_size=848, CD=None):
    """Convert world coordinates scale to pixels

    Parameters
    ----------
    ra, dec: float
        ? coordinates
    ra0, dec0: float
        reference coordinates
    scale: float, optional
        pixel scale
    im_size: float, optional
        size of the image
    CD: ?, optional
        ??

    Returns
    -------
    x, y: float
        pixel corresponding to input coordinates
    """
    if CD is not None:
        pixvec = CD.I * np.matrix([[(ra - ra0) * np.cos(dec / 180. * np.pi)],
                                   [dec - dec0]])
        x = pixvec[0, 0] + im_size / 2.
        y = pixvec[1, 0] + im_size / 2.
    else:
        x = -deg2pix(ra - ra0, scale) * np.cos(dec / 180. * np.pi)
        x += im_size / 2.
        y = deg2pix(dec - dec0, scale) + im_size / 2.

    return x, y


def SDSS_coverage(ra, dec):
    """Check if the position at ``ra``, ``dec`` is within the SDSS footprint

    Parameters
    ----------
    ra, dec: float
        coordinates to query in degrees

    Returns
    -------
    bool:
        whether the input coordinates are within the SDSS footprint
    """
    url_sdssCoverage = 'http://www.sdss3.org/dr9/index.php'
    request_sdssCoverage = urllib.urlencode({'coverageRA': ra,
                                             'coverageDec': dec})
    for line in urllib.urlopen(url_sdssCoverage, request_sdssCoverage):
        if 'overlaps with the SDSS DR9 survey area.' in line:
            return True
    return False


def plotFocalPlaneQuicklook(dra, ddec, pa, scale, ifu_centers, ra, dec, CD,
                            im_size, color='green', linewidth=0.2):
    """Patrol circles collection

    Plot the region of IFUs and patrol circle and return as a
    :class:`~matplotlib.collections.PatchCollection`, which can be added to a
    plot using :meth:`~matplotlib.Axes.add_collection`.

    Parameters
    ----------
    dra, ddec: float
        ? coordinates
    pa: float
        ?
    scale: float
        pixel scale
    ifu_centers: list
        list of ifu coordinates?
    ra, dec: flat
        reference coordinates
    CD: ?
        ??
    im_size: float
        size of the image
    color: matplotlib color, optional
        color of the circles
    linewidth: float, optional
        width of the line of the circles

    Returns
    -------
    :class:`~matplotlib.collection.PatchCollection` instance
        collection of patrol circles

    .. todo::

        `ifu_size` is hard coded to 0.012. Move to optional argument

        Rename the function: function does not plot!
    """
    ifu_size = 0.012
    patches = []
    rpa = pa / 180. * np.pi

    # plot all IFU regions
    for c in ifu_centers:

        xr, yr = wcs2pix(c[0], c[1], ra, dec, CD=CD, scale=scale,
                         im_size=im_size)

        # still need to correct the xr?
        rpol = RegularPolygon((xr, yr), 4,
                              radius=deg2pix(ifu_size, scale) / np.sqrt(2.),
                              orientation=rpa - np.pi / 4., linewidth=100.)
        patches.append(rpol)

    return PatchCollection(patches, edgecolor=color, facecolor='none')


def get_image(ra, dec, pa, size, ifu_centers, yflip, outdir):
    """Create the SDSS image around the given coordinates

    Parameters
    ----------
    ra, dec: float
        coordinates of the plot
    pa: ?
        ??
    size: float
        ??
    ifu_centers: list
        list of ifu coordinates?
    yflip: bool
        flip the image around the y axis
    outdir: string
        output directory

    Returns
    -------
    outfile: string
        full name of the saved plot


    .. todo::
        ``filename``: is hard coded. Instead of the output directory pass the
        full output name in the function arguments

        Rename the function: probably ``plot_image`` would be more appropriate

        ``box``, ``size_cut_out``: they should not be hard coded

        html size should not be hard code
    """
    filename = "quicklook_sky_%f_%f_%f.jpeg" % (ra, dec, pa)
    filename = os.path.join(outdir, filename)

    # Size in degrees
    imarray, CD, url, img_src = retrieve_image(ra, dec, size, yflip)

    size_pix = len(imarray)
    scale = deg2pix(size, scale=size_pix)

    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1], frameon=False)

    coll = plotFocalPlaneQuicklook(0, 0, pa, scale, ifu_centers, ra, dec, CD,
                                   size_pix, color='green')
    ax.add_collection(coll)
    ax.imshow(imarray, origin='lower', cmap='gray', interpolation="nearest")
    ax.axis('off')
    tempfile = ft.prefix_filename(filename, "temp_")
    fig.savefig(tempfile, bbox_inches='tight')
    plt.close(fig)

    # Convert array to Image object
    img = Image.open(tempfile)

    # Cut out the 600x600 image part of the plot
    box = (42, 8, 642, 608)
    imgCrop = img.crop(box)
    size_cut_out = 600.0

    # Set size to get 25 arcseconds per pixel - hardcoded scale of the HTML
    # interface
    rescale = int(size_cut_out * 25.0 / scale)
    imgCrop.resize((rescale, rescale))

    # Match position angle
    rotImg = imgCrop.rotate(-1.0 * pa)

    # Finally trim the image to be the correct dimensions for the 478 width by
    # 586 height html div
    xsize, ysize = rotImg.size
    left = (xsize - 478) / 2
    right = xsize - (xsize - 478) / 2
    top = (ysize - 586) / 2
    bottom = ysize - (ysize - 586) / 2

    rotImgCrop = rotImg.crop((left, top, right, bottom))
    finalImg = rotImgCrop.filter(ImageFilter.SMOOTH)
    finalImg.save(filename, "JPEG")
    os.remove(tempfile)

    return filename


def retrieve_image(ra, dec, size, yflip):
    """Wrapper function for retrieving image from SDSS. If region outside SDSS
    converage, it uses DSS image instead.

    Parameters
    ----------
    ra, dec: float
        center (?) coordinates in degrees
    size: float
        size in degrees of the patch to retrieve
    yflip: bool
        flip the image around the y axis

    Returns
    -------
    imarray: nd array
        retrieved image
    CD: numpy matrix
        ??
    url: string
        url of the request
    string
        source of the image
    """
    if SDSS_coverage(ra, dec):
        return retrieve_image_SDSS(ra, dec, size, yflip)
    else:
        return retrieve_image_DSS(ra, dec, size, yflip)


def retrieve_image_SDSS(ra, dec, size, yflip):
    """Retrieve image from ``SDSS-DR9`` or dss server (jpeg) and returns the
    image array and the url. Note that the transformation from world coordinate
    (``ra``, ``dec``) to pixel position (``x``, ``y``) is simple projection
    without rotation

        x = -scale * (ra - ra0) * cos(dec) + x0
        y =  scale * (dec - dec0) + y0

    Parameters
    ----------
    ra, dec, size, yflip:
        same as :func:`~retrieve_image`

    Returns
    -------
    same as :func:`~retrieve_image`

    .. todo::
        either catch errors from :meth:`~urllib.urlopen` or add the notion that
        it's raised and do something about it in :func:`~get_image`

        ``scale``: should be hard coded?
    """

    url_sdss_jpeg = 'http://skyservice.pha.jhu.edu/DR9/ImgCutout/getjpeg.aspx'
    # pixel scale in arcsec/pixel (1.698 for matching the dss image)
    scale = 1.698
    size_pix = int(size * 3600. / scale)
    # options for the finding chart (see
    # http://skyserver.sdss3.org/dr9/en/tools/chart/chart.asp)
    opt = 'GL'

    if size_pix > 2048:
        size_pix = 2048
        scale = size * 3600. / size_pix
    query = {'ra': ra, 'dec': dec, 'scale': scale, 'height': size_pix,
             'width': size_pix, 'opt': opt}
    request_sdss = urllib.urlencode(query)
    imfile = urllib.urlopen(url_sdss_jpeg, request_sdss)

    imarray = plt.imread(StringIO(imfile.read()), format='jpeg')

    if yflip:
        imarray = imarray[::-1, :]

    CD = np.matrix([[-1.*scale/3600., 0], [0, 1.*scale/3600.]])
    return imarray, CD, url_sdss_jpeg+'?'+request_sdss, 'SDSS'


def retrieve_image_DSS(ra, dec, size, yflip):
    """Retrieve image from dss server (fits) and return the image array, the
    url, and the CD matrix (there is rotation in DSS images). ``CD`` matrix
    transforms the pixel position (``x``, ``y``) to world coordinate (``ra``
    ,``dec``).

    Parameters
    ----------
    ra, dec, size, yflip:
        same as :func:`~retrieve_image`

    Returns
    -------
    same as :func:`~retrieve_image`

    .. todo::
        either catch errors from :meth:`~urllib.urlopen` or add the notion that
        it's raised and do something about it in :func:`~get_image`
    """

    url_dss = 'http://archive.eso.org/dss/dss/image'
    query = {'ra': ra, 'dec': dec, 'x': size*60, 'y': size*60,
             'mime-type': 'download-fits'}
    request_dss = urllib.urlencode(query)

    request_url = url_dss+'?'+request_dss

    with fits.open(request_url) as hdulist:
        hdu = hdulist[0].header
        imarray = hdulist[0].data
        if yflip:
            imarray = imarray[::-1, :]
        CD = np.matrix([[hdu['CD1_1'], hdu['CD1_2']],
                        [hdu['CD2_1'], hdu['CD2_2']]])

    return imarray, CD, request_url, 'DSS'
