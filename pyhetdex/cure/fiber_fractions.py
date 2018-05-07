# Misc python library to support HETDEX software and data analysis
# Copyright (C) 2016  "The HETDEX collaboration"
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
from __future__ import print_function, absolute_import

# import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from numpy import clip, zeros, arange, pi, arccos, sqrt, array, power
# from numpy import log10, abs
from numpy.linalg import norm
from astropy.modeling import models
from pyhetdex.het.dither import ParseDither
from pyhetdex.het.ifu_centers import IFUCenter


# def moffat_generator(cx, cy, fwhm):
#
#     beta = 2.5;
#     alpha = fwhm /2.0/ sqrt(power(2.0,(1.0/beta)) - 1.0)
#     a2 = alpha*alpha;
#     n = (beta-1.0)/(pi*a2);
#
#     print(alpha)
#
#     def moffat(x, y):
#         r2 = (x-cx)*(x-cx) + (y-cy)*(y-cy)
#
#         index = (abs(x - -6.0804) < 0.1) & (abs(y - -6.1) < 0.1)
#         print(zip(x[index], y[index], r2[index],
#                   n*power(1.0 + (r2[index]/a2), -beta)))
#
#         return n*power(1.0 + (r2/a2), -beta)
#
#     return moffat


def intersect_area(ra, rb, d):
    """
    Compute the overlapping area between two circles

    Formula derivation based on
    http://mathworld.wolfram.com/Circle-CircleIntersection.html

    Parameters
    ----------
    ra, rb : float
        the radii of the two circles
    d : float
        the distance between the two circles centres
    """
    # make sure ra is always the biggest
    if rb > ra:
        temp = ra
        ra = rb
        rb = temp

    rb2 = rb*rb

    # rb is completely enclosed
    if d + rb < ra:
        return pi*rb2

    ra2 = ra*ra
    d2 = d*d
    arg1 = (d2 + ra2 - rb2)/(2.0*d)
    arg2 = (d2 + rb2 - ra2)/(2.0*d)

    # rb's center is outside of ra:
    if d > ra:
        area1 = ra2*arccos(clip(arg1/ra, -1.0, 1.0)) - arg1*sqrt(max(ra2 - arg1*arg1, 0.0))
        area2 = rb2*arccos(clip(arg2/rb, -1.0, 1.0)) - arg2*sqrt(max(rb2 - arg2*arg2, 0.0))

        return area1 + area2

    # rb's center inside, but still overlap
    else:
        arg2 = -1.0*arg2
        area1 = ra2*arccos(clip(arg1/ra, -1.0, 1.0)) - arg1*sqrt(max(ra2 - arg1*arg1, 0.0))
        area2 = rb2*arccos(clip(arg2/rb, -1.0, 1.0)) - arg2*sqrt(max(rb2 - arg2*arg2, 0.0))

        return pi*rb2 - (area2 - area1)

    return  # area


class ModelFrac(object):
    """ Class used to cache the calculations of how much
        PSF model flux is contained in a fiber of a certain distance.

        Parameters
        ----------
        fwhm : float
            the FWHM of the PSF
        tpsf_model : string
            the name of the PSF model to use (e.g. gaussian, moffat)
        fiber_r : float
            the radius of the fiber
        imagesize : float
            the size of the image (in the same units as fwhm, fiber_r),
            determines how far out the PSF is integrated
        pix_arcsec : float
            the number of pixels per unit length for the
            psf image (in the same units as fwhm, fiber_r), determines
            the accuracy of the integration of the PSF (bigger numbers,
            more accuracy)

    """
    def __init__(self, fwhm, tpsf_model, fiber_r, imagesize=20, pix_arcsec=10):

        self.fwhm = fwhm
        self.fiber_r = fiber_r
        self.imagesize = imagesize
        self.pix_arcsec = pix_arcsec

        # hard coded in cure
        self.offsets = 6.0*fiber_r*(arange(0, 100)/100.0)

        if tpsf_model == 'gaussian':
            sigma = fwhm/2.35
            self.psf_model = models.Gaussian2D(x_stddev=sigma,
                                               y_stddev=sigma)
        elif tpsf_model == 'moffat':
            alpha = 2.5  # hard coded in Cure
            gamma = fwhm/2.0/sqrt(power(2.0, (1.0/alpha)) - 1.0)
            self.psf_model = models.Moffat2D(alpha=alpha,
                                             gamma=gamma)
            # self.psf_model = moffat_generator(0.0, 0.0, fwhm)

        else:
            # model not supported
            return

        self.initialise_modelfrac()

    def initialise_modelfrac(self):
        """ Cache the fractions of PSF flux contained in fibers
            and store the values as a function of fiber
            distance
        """
        imagedim = int(self.imagesize*self.pix_arcsec)

        # xcen = imagedim/(2.0*self.pix_arcsec)
        # ycen = xcen
        xs = []
        ys = []

        # method designed to perfectly match Cure
        frm = -self.imagesize/2
        to = self.imagesize/2
        step = (to - frm)/(imagedim - 1.0)

        for ix, x in enumerate(range(0, imagedim)):
            for iy, y in enumerate(range(0, imagedim)):

                xs.append(frm + step*ix)
                ys.append(frm + step*iy)

        ys = array(ys)  # - ycen - (10 - 9.949797)
        xs = array(xs)  # - xcen - (10 - 9.949797)

        # Produce an image of the PSF
        self.psf_image = self.psf_model(ys, xs).reshape(imagedim*imagedim)
        self.psf_image = self.psf_image/sum(self.psf_image)

        # plt.imshow(self.psf_image.reshape(imagedim, imagedim))
        # plt.show()

        self.modelfracs = []
        for offset in self.offsets:

            # create a mask of the fiber
            self.distmap = norm(list(zip(ys, xs - offset)), axis=1)
            self.mask = zeros(imagedim*imagedim)
            self.mask[self.distmap < self.fiber_r] = 1.0

            # compute the masked PSF flux
            masked = self.mask*self.psf_image
            self.modelfracs.append(sum(masked))

        # from numpy import log10
        # plt.imshow(log10(masked.reshape(imagedim, imagedim)))
        # plt.show()

        self.func = interp1d(self.offsets, self.modelfracs, fill_value=0.0)

    def __call__(self, offset):
        """ Return the fraction of PSF model flux
            contained in a fiber that is a distance of
            offset away from the source
        """
        return(self.func(offset))


class FiberFracMap(object):
    """ Class for returning the fraction of model fluxes in apertures,
        the fraction of fibers in apertures and combinations therein which
        are needed for the prediction of SNR ratio distributions.

        Parameters
        ----------
        ifu_cen_file, dither_file : string
            filename of an IFU cen file and dither file for this IFU
        psf_type : string
            the name of the PSF model to use (for the ModelFrac object)
    """

    def __init__(self, ifu_cen_file, dither_file, psf_type="moffat"):

        self.ifucen = IFUCenter(ifu_cen_file)
        self.fiber_r = self.ifucen.fiber_d*0.5
        self.fiber_a = self.fiber_r*self.fiber_r*3.14159265
        self.dither = ParseDither(dither_file)
        self.psf_type = psf_type

        self.psf_models = []
        for fwhm in self.dither.seeing.values():
            self.psf_models.append(ModelFrac(fwhm, self.psf_type,
                                             self.fiber_r))

    def return_fiberfrac(self, xs, ys, detection_aperture_r, min_thresh=0.1):
        """ Returns various combinations of the fraction of fibers in the
            detection aperture, the fraction of the model flux in the
            detection aperture and so on.

            Parameters
            ----------
            x, y : float array
                position of the detection aperture
            detection_aperture_r :
                radius of the detection aperture
            min_thresh : float, optional
                lowest fraction of a fiber in the aperture needed
                for it to be considered

            Returns
            -------
            fiber_frac : float
                sum of the fraction of the fiber in an aperture, over
                all fibers
            fiber_frac2 : float
                sum of the squared fraction of the fiber in an aperture, over
                all fibers
            fluxfrac : float
                fraction of model flux in the detection aperture (same as
                fluxfrac output by detect)
            fiberfluxfrac : float
                sum of the product of fiber_frac and model frac over the
                fibers. Needed to compute the actual measured flux from the
                total flux
            ffiberfluxfrac : float
               sum of the product of fiber_frac squared and model frac over the
               fibers.
        """

        ap_r = detection_aperture_r
        sepmin = ap_r + self.fiber_r

        fluxfracs = []
        fiberfracs = []
        fiberfrac2s = []
        fiberfluxfracs = []
        ffiberfluxfracs = []

        for x, y in zip(xs, ys):
            fluxfrac = 0
            fiberfrac = 0
            fiberfrac2 = 0
            fiberfluxfrac = 0
            ffiberfluxfrac = 0

            for dx, dy, psf_model_frac in zip(self.dither.dx.values(),
                                              self.dither.dy.values(),
                                              self.psf_models):
                ap_pos = [x - dx, y - dy]

                for channel in ['L', 'R']:
                    fiber_pos = list(zip(self.ifucen.xifu[channel],
                                         self.ifucen.yifu[channel]))
                    for fiber_pos in fiber_pos:

                        d = norm(array(ap_pos) - array(fiber_pos))

                        if d < sepmin:
                            mfrac = psf_model_frac(d)
                            area = intersect_area(ap_r, self.fiber_r, d)/self.fiber_a

                            if area > min_thresh:
                                fiberfrac += area
                                fiberfrac2 += area*area
                                fluxfrac += mfrac
                                fiberfluxfrac += mfrac*area
                                ffiberfluxfrac += mfrac*area*area

            fluxfracs.append(fluxfrac)
            fiberfracs.append(fiberfrac)
            fiberfrac2s.append(fiberfrac2)
            fiberfluxfracs.append(fiberfluxfrac)
            ffiberfluxfracs.append(ffiberfluxfrac)

        return (array(fiberfracs), array(fiberfrac2s), array(fluxfracs),
                array(fiberfluxfracs), array(ffiberfluxfracs))
