"""
Fits the point-like continuum detections with the Moffat distribution and
returns alpha, beta and FWHM for the required detections.

The Moffat distribution is defined in:
http://en.wikipedia.org/wiki/Moffat_distribution
"""

from __future__ import print_function, absolute_import

import itertools as it

import numpy as np
import scipy.optimize as spo


# ==== The Moffat distribution ==== #
def moffat(x, y, alpha, beta, ampl, xc, yc):
    """
    Implementation of the 2D Moffat distribution
    Parameters
    ----------
    x, y: floats
        where to evaluate the Moffat
    alpha, beta: floats
        parameters
    xc, yc: floats
        coordinates of the center
    ampl: float
        overall normalisation
    output
    ------
    moff: float
        Moffat(x, y)
    """
    norm = ampl * (beta - 1) * (np.pi * alpha**2) ** (-1)
    return norm * (1 + ((x - xc)**2 + (y - yc)**2) * alpha**(-2)) ** (-beta)


def get_fwhm(alpha, beta):
    """
    Compute the fwhm given alpha and beta
    Parameters
    ----------
    alpha, beta: floats or nd arrays
        parameters
    output
    ------
    fwhm: float or nd array
        full width half max
    """
    return 2. * alpha * np.sqrt(2**(1/beta) - 1)


# ==== The integration ==== #
class BaseSampler(object):
    """
    Sample each IFU with the given number of points. It caches the sampled
    IFUs.
    This is the base sampler and doesn't do the sampling. It provides a
    function that returns the list of points for a given circle center and
    radius. Anyway remember to call the init in any of the subclasses, as it
    initialise the cache
    """

    def __init__(self):
        """
        Initialise the variable used.
        _xs and _ys should be properly defined in the derived classes
        """
        self._cache = {}
        self._xs, self._ys = None, None

    def get_samples(self, x, y, r):
        """
        Get the sample point for the circle centered in (*x*, *y*) with radius
        *r*
        Parameters
        ----------
        x, y: floats
            center of the circle
        r: float
            radius of the circle
        output
        ------
        xs, ys: ndarray
            points sampling the circle
        """
        # create an string id for the given circle. Discard any difference
        # between the fourth digit
        _id = "{0:.4f}_{1:.4f}_{2:.4f}".format(x, y, r)
        try:
            return self._cache[_id]
        except KeyError:
            # rescale to the correct radius and shift the sample points
            _xs, _ys = self._xs * r, self._ys * r
            _xs, _ys = _xs + x, _ys + y
            # save the new values in the cache
            self._cache[_id] = (_xs, _ys)
            return _xs, _ys


class RandomSampler(BaseSampler):
    """
    Randomly sample the circle
    """

    def __init__(self, n_points):
        """
        Creates about *n_points* random (x, y) coordinates that sample the unit
        circle (x=0, y=0, r=0.5). It first creates a unite square (a=1) and
        then removes the points outside the circle
        Parameters
        ----------
        n_points: int
            approximate number of points
        """
        super(RandomSampler, self).__init__()

        _n_points = n_points * 4. / np.py
        xy = np.random.random(size=[2, _n_points]) - 0.5
        # find all the points in a circle of radius 0.5
        in_circle = (xy**2).sum(axis=0) < 0.25
        self._xs, self._ys = xy[:, in_circle]


class GridSampler(BaseSampler):
    """
    Regular grid sample the circle
    """

    def __init__(self, n_points):
        """
        Creates about *n_points* (x, y) coordinates in a regular that sample
        the unit circle (x=0, y=0, r=0.5). It first creates a unite square
        (a=1) and then removes the points outside the circle.
        The actual number of points is going to be almost:
        round(sqrt(n_points * 4/pi)) ** 2
        Parameters
        ----------
        n_points: int
            approximate number of points
        """
        super(GridSampler, self).__init__()

        _n_points = np.around(np.sqrt(n_points * 4 / np.pi))
        x = np.linspace(-0.5, 0.5, num=_n_points)
        x, y = np.meshgrid(x, x)
        x, y = x.flatten(), y.flatten()
        # find all the points in a circle of radius 0.5
        in_circle = (x**2 + y**2) < 0.25
        self._xs = x[in_circle]
        self._ys = y[in_circle]


# ==== Montecarlo like integration ==== #
def montecarlo_2d(func, xy, area, params=()):
    """
    Compute the 2 dimensional integral of function *func* using a simple
    montecarlo-like integration.
    Parameters
    ----------
    func: callable
        2-dimensional function to evaluate: f(x, y, *params)
    xy: tuple or list of two arrays of size N or (2, N) array
        x and y coordinates of the points to use to compute the integral
    area: float
        area sampled by *xy*
    params: list
        parameters to pass to *func*
    output
    ------
    I: float
        integral
    sI: float
        error on the integral
    """
    x, y = xy  # unpack
    f_xy = func(x, y, *params)
    # evaluate the integral and its error
    I = area * f_xy.mean()
    sI = area * f_xy.std(ddof=1) / np.sqrt(x.size)
    return I, sI


# ==== Residual ==== #
def residuals(params, func, zmeas, x, y, r, sampler):
    """
    Given the parameters, computes the integral of *func* using the 2d
    montecarlo integration and returns the difference with the measured *z*.
    *x*, *y* and *r* are used to get the coordinated for the integration from
    *sampler*
    Parameters
    ----------
    params: list
        parameters to pass to the Moffat
    func: callable
        2-dimensional function to evaluate: f(xsam, ysam, *params), where
        *xsam* and *ysam* as extracted from *sampler*
    zmeas: 1d array
        measured value
    x, y, r: 1d arrays
        centers and radii of the circle to use as domain for the integral
    sampler: BaseSampler instance
        get the coordinates to use to estimate the integral
    output
    ------
    residuals: 1d array
        measurement minus model
    """
    residuals = np.empty_like(zmeas)

    for i, x_, y_, a_, z_ in zip(it.count(), x, y, np.pi * r**2, zmeas):
        xsam, ysam = sampler.get_samples(x_, y_, a_)
        model = montecarlo_2d(func, [xsam, ysam], a_, params=params)
        residuals[i] = z_ - model[0]

    return residuals


def seeing_minimizer(residual, func, init_params, ifuhead, detection,
                     sampler, selection_radius=5, ifuhead_kwargs=None,
                     lsq_kwargs=None):
    """
    Run the least square minimisation based on the *residual* of the function
    *func*
    Parameters
    ----------
    residual: callable
        function that estimates the residual and that is passed to the least
        square minimize. Signature:
            residual(params, func, z, x, y, sampler)
                params: parameter set
                func: *func*
                z: measured value (the integrate fiber flux from *ifuhead*)
                x, y, r: center and radius of the circles where to do the
                integration of *func* (centers and radii of the fibers from
                    *focalplane*)
                sampler: instance used to sample the circles (fibers)
    func: callable
        2-dimensional function to be integrated Signature:
            func(xsam, ysam, *params), where
                xsam, ysam: coordinates sampling the fibers. Retrieved from
                    *sampler* and *x*, *y*, *r*
    init_params: list
        Initial parameters to pass to *func*
    ifuhead: reconstruct_ify.ReconstructedIFU instance. Contains the
        position, size and flux of the fibers in the focal plane
    detection: instance with the 'icx', 'icy', 'fwhm_xy' fields
        e.g.: quicklook:src.detection.PContDetection
    selection_radius: float
        all the fibers in *focalplane* within *selection_radius* x
        *detection.fwhm_xy* are selected
    sampler: BaseSampler instance
        get the coordinates to use to estimate the integral
    ifuhead_kwargs: dictionary
        options to pass to ifuhead.reconstruct ('wmin', 'wmax')
    lsq_kwargs: dictionary
        options to pass to the leastsq function
    output
    ------
    result: whatever leastsq returns
        see
        http://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.leastsq.html
    """

    # get the reconstructed IFU head
    if ifuhead_kwargs is None:
        ifuhead_kwargs = {}
    x_fibs, y_fibs, flux_fibs = ifuhead.reconstruct(**ifuhead_kwargs)

    # find the fibers to use for the fit
    used_fibers = ((x_fibs - detection.icx)**2 + (y_fibs - detection.icy)**2)
    used_fibers = used_fibers <= selection_radius * detection.fwhm_xy
    x_fibs = x_fibs[used_fibers]
    y_fibs = y_fibs[used_fibers]
    flux_fibs = flux_fibs[used_fibers]

    # do the fit
    if lsq_kwargs is None:
        lsq_kwargs = {}
    else:  # if there is any "args" key drop it
        lsq_kwargs.pop("args", None)
    # standard least square
    radii = np.ones_like(x_fibs) * ifuhead.fiber_d/2.
    args = (func, flux_fibs, x_fibs, y_fibs, radii, sampler)
    result = spo.leastsq(residual, init_params, args=args, **lsq_kwargs)

    return result


def main():
    """
    Mock main to show how to use it
    """
    import reconstruct_ifu as rci
    # define sampler
    sampler = GridSampler(10000)
    # get the detection
    detection = "get the detection from quicklook"
    # set up the IFU head
    ifuhead = rci.ReconstructedIFU("IFU_cent_file", dither_file="dither_file",
                                   fextract=["Fejpes1.fits", "Fejpes2.fits",
                                             "Fejpes3.fits", "Fejpes4.fits",
                                             "Fejpes5.fits", "Fejpes1.fits"])

    fit = seeing_minimizer(residuals, montecarlo_2d,
                           [2, 2, 10, detection.icx, detection.icy], ifuhead,
                           detection, sampler,
                           ifuhead_kwargs={'wmin': 4000, "wmax": 5000},
                           sq_kwargs={'full_output': True, 'epsfcn': 1e-3})
