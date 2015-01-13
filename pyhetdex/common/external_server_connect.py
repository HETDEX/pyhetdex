"""

Download a SDSS or DSS image of the focal plane to display in
quicklook.

Largely copied from hetdexshuffle/visualize.py with some minor modifications

"""

import urllib 
from StringIO import StringIO

import Image
from ImageFilter import SMOOTH

import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from matplotlib.collections import PatchCollection

try:
    from astropy.io import fits
except ImportError:
    import pyfits as fits

from numpy import *


def deg2pix(degree, scale=1.698):
    return degree*3600./scale


def wcs2pix(ra, dec, ra0, dec0, scale=1.698, im_size=848, CD=None):
    if CD != None:
        pixvec = CD.I*matrix([[(ra-ra0)*cos(dec/180.*pi)],[dec-dec0]])
        x = pixvec[0,0] + im_size/2.
        y = pixvec[1,0] + im_size/2.
    else:
        x = -deg2pix(ra-ra0,scale)*cos(dec/180.*pi) + im_size/2.
        y = deg2pix(dec-dec0,scale) + im_size/2.

    return x,y


def SDSS_coverage(ra,dec):
    url_sdssCoverage = 'http://www.sdss3.org/dr9/index.php'
    request_sdssCoverage = urllib.urlencode({'coverageRA':ra, 'coverageDec':dec})
    for line in urllib.urlopen(url_sdssCoverage, request_sdssCoverage):
        if 'overlaps with the SDSS DR9 survey area.' in line:
            return True
    return False

def plotFocalPlaneQuicklook(dra, ddec, pa, scale, ifu_centers, ra, dec, CD, im_size, color='green', linewidth=0.2):
    """
    Plot the region of IFUs and patrol circle and return as a PatchCollection,
    which can be added to axes by axes.add_collection.
    """

    ifu_size = 0.012
    patches = []
    rpa = pa/180.*pi
    
    #plot all IFU regions
    for c in ifu_centers:

        xr, yr = wcs2pix(c[0], c[1], ra, dec, CD=CD, scale=scale, im_size=im_size)

        #still need to correct the xr?
        patches.append( RegularPolygon((xr,yr),4,radius=deg2pix(ifu_size, scale)/sqrt(2.), orientation=rpa-pi/4.,linewidth=100.0 ) )

    return PatchCollection(patches, edgecolor=color, facecolor='none')


def get_image(ra, dec, pa, size, ifu_centers, yflip):
    #Size in degrees
    filename="quicklook_sky_%f_%f_%f.jpeg"%(ra, dec, pa)
    imarray, CD, url, img_src = retrieve_image(ra,dec,size,yflip)
    
    size_pix = len(imarray)
    scale = size*3600./size_pix
    
    fg = plt.figure()
    ax = fg.add_axes([0,0,1,1], frameon=False)
    
    ax.add_collection(plotFocalPlaneQuicklook(0, 0, pa, scale, ifu_centers, ra, dec, CD, size_pix, color='green'))
    ax.imshow(imarray, origin='lower', cmap='gray', interpolation="nearest")
    plt.axis('off')
    plt.savefig( "html/temp_" + filename, bbox_inches='tight')

    #Convert array to Image object
    img = Image.open( "html/temp_" + filename )
    
    #Cut out the 600x600 image part of the plot
    box = (42, 8, 642, 608)
    imgCrop = img.crop(box)
    size_cut_out = 600.0

    #Set size to get 25 arcseconds per pixel - hardcoded scale of the HTML interface
    rescale = int(size_cut_out*25.0/scale)
    imgCrop.resize((rescale,rescale))
    
    #Match position angle
    rotImg = imgCrop.rotate(-1.0*pa)
    
    #Finally trim the image to be the correct dimensions for the 478 width by 586 height html div
    xsize,ysize = rotImg.size
    left = (xsize - 478)/2
    right = xsize - (xsize - 478)/2
    top = (ysize - 586)/2
    bottom  = ysize - (ysize - 586)/2
    
    finalImg = rotImg.crop((left, top, right, bottom)).filter(SMOOTH)
    finalImg.save("html/" + filename, "JPEG")

    return filename 


def retrieve_image(ra,dec,size,yflip):
    """
    Wrapper function for retrieving image from SDSS. If region outside SDSS
    converage, it uses DSS image instead.
    (ra, dec, size) in degree
    """
    if SDSS_coverage(ra,dec):
        return retrieve_image_SDSS(ra,dec,size,yflip)
    else:
        return retrieve_image_DSS(ra,dec,size,yflip)
    
    
    
def retrieve_image_SDSS(ra,dec,size,yflip):
    """
    Load image from sdss-dr9 or dss server(jpeg) and return the image array
    and the url. Note that the transformation from world coordinate(ra,dec) to
    pixel position(x,y) is simple projection without rotation, i.e.
    x=-scale*(ra-ra0)*cos(dec)+x0; y=scale*(dec-dec0)+y0
    
    size in degrees
    
    """

    url_sdssJPEG = 'http://skyservice.pha.jhu.edu/DR9/ImgCutout/getjpeg.aspx'
    scale         = 1.698 #pixel scale in arcsec/pixel (1.698 for matching the dss image)
    size_pix    = int(size*3600./scale) 
    opt        = 'GL'    #options for the finding chart (see http://skyserver.sdss3.org/dr9/en/tools/chart/chart.asp )
    
    if size_pix > 2048:
        size_pix = 2048
        scale = size*3600./size_pix    
    request_sdss = urllib.urlencode({'ra':ra, 'dec':dec, 'scale':scale, 'height':size_pix, 'width':size_pix, 'opt':opt})
    #url = "http://skyservice.pha.jhu.edu/DR9/ImgCutout/getjpeg.aspx?"+request_sdss
    imfile = urllib.urlopen(url_sdssJPEG, request_sdss)
    imarray = plt.imread(StringIO(imfile.read()), format='jpeg')
    if yflip:
        imarray = imarray[::-1,:]    
    CD = matrix([[-1.*scale/3600., 0 ], [0, 1.*scale/3600.]])
    return imarray, CD , url_sdssJPEG+'?'+request_sdss, 'SDSS'


def retrieve_image_DSS(ra,dec,size,yflip):
    """
    Load image from dss server(fits) and return the image array, the url, and
    the CD matrix (there is rotation in DSS images).
    CD matrix transforms the pixel position(x,y) to world coordinate(ra,dec).
    """

    url_dss = 'http://archive.eso.org/dss/dss/image'
    #request_dss = urllib.urlencode({'ra':ra, 'dec':dec, 'x':size*60, 'y':size*60, 'mime-type':'download-gif'})
    request_dss = urllib.urlencode({'ra':ra, 'dec':dec, 'x':size*60, 'y':size*60, 'mime-type':'download-fits'})
    #url = "http://archive.eso.org/dss/dss/image?"+request_dss
    #imfile = urllib.urlopen(url_dss, request_dss)
    #imarray = plt.imread(StringIO(imfile.read()), format='gif')
    #print url_dss+'?'+request_dss_fits
    hdulist = fits.open(url_dss+'?'+request_dss)
    hdu = hdulist[0].header
    imarray = hdulist[0].data
    if yflip:
        imarray = imarray[::-1,:]    
    CD = matrix([[hdu['CD1_1'], hdu['CD1_2']], [hdu['CD2_1'], hdu['CD2_2']]])
    return imarray, CD, url_dss+'?'+request_dss, 'DSS'


    