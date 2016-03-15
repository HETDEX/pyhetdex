"""
Convert a HETDEX datacube into an RGB image

AUTHOR: Daniel Farrow <dfarrow@mpe.mpg.de>
"""
from __future__ import print_function

from numpy import nanmax, nanmin, zeros, flipud, fliplr
from PIL import Image
from astropy.io.fits import getdata, getheader 
from astropy.visualization import SqrtStretch

class WavelengthConversion(object):
    """  
    Class to find the wavelength of an image
    in the datacube.

    Parameters
    ----------
    header : dict
        a dictionary (or similar) of header values, related
        to the spectral axis
    """
    
    def __init__(self, header):

        # XXX read in wavelength solution from header here
        self.start = 3500
        self.step = 0.968992233276367

    def pix2lmbda(self, pix):
        """
        Return wavelength of pix along
        spectral axis
        """

        return pix*self.step + self.start  


class TophatFilter(object):
    """
    Simple filter to use when creating colour
    images. Returns 1 for wavelengths between
    lower_cut and upper_Cut

    Parameters
    ----------
    lower_cut, upper_cut : float
        the limits of the top hat

    Returns
    -------
    value : float
        1 if lower_cut<input<upper_cut, 0 otherwise
    """

    def __init__(self, lower_cut, upper_cut):

        self.lower_cut = lower_cut
        self.upper_cut = upper_cut

    def __call__(self, lmbda):
 
        if lmbda > self.lower_cut and lmbda < self.upper_cut:
            return 1.0
        else:
            return 0.0



class NormalizeClipped():
    """
    Normalize an input array, then apply
    a sqrt stretch. Clip values above vmax 
    to 1.0 and below vmin to 0.0.

    Parameters
    ----------
    vmin, vmax : float (optional)
        range over which to clip the input

    Returns
    -------
    value : float or array
        input clipped to [0,1] with sqrt stretch applied 
    """  

    def __init__(self, vmin=None, vmax=None):
        
        self.vmin = vmin
        self.vmax = vmax
        

    def __call__(self, values):
    
        if not self.vmin:
            self.vmin = nanmin(values)

        if not self.vmax:
            self.vmax = nanmax(values)

        normed = (values - self.vmin)/(self.vmax - self.vmin)
        normed[normed > 1.0] = 0.99999
        normed[normed < 0.0] = 0.0  

        stretch = SqrtStretch()

        return stretch(normed)
                

def scaleRgbArray(input, vmin, vmax):
    """
    Scale an input 3*[N,N] array to
    a array that can be used to create
    a colour image, where the range of
    each element is [0, 255].

    Parameters
    ----------
    vmin, vmax : float
        the range to map to [0, 255]

    """

    output = zeros(input.shape, 'uint8')
    ncols = 2**8
    
    norm = NormalizeClipped(vmin=vmin, vmax=vmax)

    output[..., 0] = ncols*norm(input[..., 0])
    output[..., 1] = ncols*norm(input[..., 1])
    output[..., 2] = ncols*norm(input[..., 2])

    return output

def create_rgb_image_from_cube(fname, blue_filter=TophatFilter(3500, 4166), 
                               green_filter=TophatFilter(4166, 4832), 
                               red_filter=TophatFilter(4832,5500), 
                               fout=None, vmin=None, vmax=None,
                               outdims=(500,500)):
    """
    Turn a VIRUS image cube into a colour image.

    Parameters
    ----------
    fname : string
        filename of datacube
    red_filter, green_filter, blue_filter : callable (optional)
        a function that when called returns the filter transmission
        for a particular wavelength for the three colour image
        channels
    fout : string (optional)
        filename to output to
    vmin, vmax : float (optional)
        a range over which to stretch the image, values outside
        this range clipped  
    outdims : tuple of floats (optional)
        output dimensions of Image      

    Returns
    -------
    image : PIL.Image class
        your colour image

    """

    # open the file and read it
    try:
        with open(fname, 'rb') as fp:
            cube = getdata(fname)
            wavelength_conversion = WavelengthConversion(getheader(fname))
    except IOError as e:
        print("Error opening file {:s}. Error follows {:s}".format(fname, e)) 
        return None

    # blank array to store the image
    rgbArray = zeros((cube[0].shape[0], cube[0].shape[1], 3))

    # integrate over the filters
    for i, image in enumerate(cube):
   
        lmbda = wavelength_conversion.pix2lmbda(i)
        rgbArray[..., 0] += image*red_filter(lmbda) 
        rgbArray[..., 1] += image*green_filter(lmbda) 
        rgbArray[..., 2] += image*blue_filter(lmbda) 


    # scale and create the image
    rgbArrayScaled = scaleRgbArray(rgbArray, vmin, vmax)
    image = Image.fromarray(rgbArrayScaled)
    image = image.resize(outdims)

    if fout:
        image.save(fout)
   
    return image


def main(args=None):
    """ Convert a data cube into a three colour image

    Example  
    -------

    datacube2rgb  CuFeobject_dither0_dwarfGal.fits test2.eps --red-filter 
                  4967 5057 --green-filter 4815 4905 --blue-filter 4631 4731 --vmin 0 --vmax 1e

    """

    from textwrap import dedent
    import argparse
    import matplotlib.pyplot as plt

    if not args:
        import sys
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description=dedent("""Convert a datacube to a colour image. Default is to split cube 
                                                        into three equal-sized colour bins. You might also try: 4631,4731 (dunno), 
                                                        4815,4905 (Hbeta), 4967,5057 (OII).  
                                                       """))

    parser.add_argument('fin', type=str, help='filename of datacube')
    parser.add_argument('fout', type=str, help='output filename')
    parser.add_argument('--vmin', type=float, default=None, help='Minimum range for image stretch')
    parser.add_argument('--vmax', type=float, default=None, help='Maximum range for image stretch')
    parser.add_argument('--axes_off', action='store_true', help="Whether or not to display axes")  
    parser.add_argument('--red-filter', type=float, default=(4832, 5500), help="Range for red filter (A)", nargs=2)
    parser.add_argument('--green-filter', type=float, default=(4166, 4832), help="Range for green filter (A)", nargs=2)
    parser.add_argument('--blue-filter', type=float, default=(3500, 4166), help="Range for blue filter (A)", nargs=2)
    inputs = parser.parse_args(args)

    print("RED filter: {:s} A".format(str(inputs.red_filter))) 
    print("GREEN filter: {:s} A".format(str(inputs.green_filter)))
    print("BLUE filter: {:s} A".format(str(inputs.blue_filter)))
 
    image = create_rgb_image_from_cube(inputs.fin,
                                       red_filter=TophatFilter(inputs.red_filter[0], inputs.red_filter[1]),
                                       green_filter=TophatFilter(inputs.green_filter[0], inputs.green_filter[1]),
                                       blue_filter=TophatFilter(inputs.blue_filter[0], inputs.blue_filter[1]),
                                       vmin=inputs.vmin, 
                                       vmax=inputs.vmax)

    if not image:
        print("Image creation failed!")
        sys.exit(1)
    
    if not inputs.axes_off:

        # show the image
        plt.imshow(image, origin='lower left', extent=(0, 49, 0, 49))

        plt.xlabel("x (arcseconds)", fontsize=18.0)
        plt.ylabel("y (arcseconds)", fontsize=18.0)
    
        ax = plt.gca()
        ax.tick_params(axis='x', labelsize=18.0) 
        ax.tick_params(axis='y', labelsize=18.0) 
    
        #plt.title("NGC 1569 (Red 5007A, Green 4865A, Blue 4681A)", fontsize=20.0)
        #plt.title("NGC 1569 (spectrograph split into 3 tophats)", fontsize=20.0)
        plt.savefig(inputs.fout)

    else:

        image = image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
        image.save(inputs.fout)





