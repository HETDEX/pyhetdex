"""Image quality fit.

.. moduleauthor:: Francesco Montesano <montefra@mpe.mpg.de>

Fits the point-like continuum detections with the Moffat distribution and
returns alpha, beta and FWHM for the required detections.

.. warning:: 
    The module does run, but it isn't tested. Should not be used before proper
    tests are implemented

References 
----------
Astropy fitting: http://astropy.readthedocs.org/en/v1.0rc2/modeling/index.html astropy.modeling
"""

from __future__ import print_function, absolute_import

from astropy.modeling.functional_models import Moffat2D
import astropy.modeling.fitting as apf

import numpy as np

import pyhetdex.het.reconstruct_ifu as precon


# ==== Helper functions ==== #
def get_fwhm(gamma, alpha):
    """Compute the fwhm given gamma and alpha

    Parameters
    ----------
    gamma, alpha: floats or nd arrays
        parameters

    Returns
    -------
    float or nd array
        full width half max
    """
    return 2. * gamma * np.sqrt(2**(1/alpha) - 1)


# ==== The integration ==== #
class _BaseSampler(object):
    """ Sample a circle and returns the samples of a circle centered in (`x`,
    `y`) and with radius `r`.

    This is the base class and doesn't do the sampling. It provides a
    :meth:`~get_samples`
    that returns the list of points for a given circle center and
    radius. Anyway remember to call the init in any of the subclasses, as it
    initialise the cache

    Parameters
    ----------
    n_points: int
        number of points to sample

    Notes
    -----
        Private attributes `_xs` and `_ys` should be appropriately defined in
        the derived classes
    """
    def __init__(self, n_points):
        self._n_points = n_points
        self._xs, self._ys = None, None
        self._cache = {}

    def get_samples(self, x, y, r=1.):
        """Get the sample point for the circle centered in (`x`, `y`) with
        radius `r`

        Parameters
        ----------
        x, y: floats
            center of the circle
        r: float
            radius of the circle

        Returns
        -------
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


class RandomSampler(_BaseSampler):
    """Randomly sample the circle

    Creates about `n_points` random (x, y) coordinates that sample the circle
    (x=0, y=0, r=1). It first creates a square with `side=2*r` and then removes
    the points outside the circle.

    Parameters
    ----------
    n_points: int
        approximate number of points
    """

    def __init__(self, n_points):
        super(RandomSampler, self).__init__(n_points)

        # do it for the unitary circle
        _n_points = n_points * 4. / np.py
        xy = 2. * np.random.random(size=[2, _n_points]) - 1.
        # find all the points in a circle of radius 0.5
        in_circle = (xy**2).sum(axis=0) < 1.
        self._xs, self._ys = xy[:, in_circle]


class GridSampler(_BaseSampler):
    """Regular grid sample the circle

    Creates about `n_points` (x, y) coordinates in a regular grid that
    samples the unit circle (x=0, y=0, r=1). It first creates a unit square
    (a=2) and then removes the points outside the circle.
    The actual number of points is going to be almost:
    `round(sqrt(n_points * 4/pi)) ** 2`

    Parameters
    ----------
    n_points: int
        approximate number of points
    """

    def __init__(self, n_points):
        super(GridSampler, self).__init__(n_points)

        _n_points = np.around(np.sqrt(n_points * 4 / np.pi))
        x = np.linspace(-1., 1., num=_n_points)
        x, y = np.meshgrid(x, x)
        x, y = x.flatten(), y.flatten()
        # find all the points in a circle of radius 1
        in_circle = (x**2 + y**2) < 1.
        self._xs = x[in_circle]
        self._ys = y[in_circle]


# ==== The model is the Moffat function integrated in circles ==== #
# This class assumes that all the fibers have the same radius, set in the
# constructor.
# TODO: implement derivative using
# http://astropy.readthedocs.org/en/stable/_modules/astropy/modeling/functional_models.html#Beta2D
class MonteCarlo_Moffat2D(Moffat2D):
    """The model is the 2D Moffat distribution integrated in circles.
    
    The integration is done in a Montecarlo like approach using the points
    provided by the sampler instance.

    Parameters
    ----------
    sampler: instance child of _BaseSampler
        sampling of a unit circle centered in (0, 0)
    radius: float
        fiber radius
    amplitude : float
        Amplitude of the model
    x_0 : float
        x position of the maximum of the Beta model
    y_0 : float
        y position of the maximum of the Beta model
    gamma : float
        Core width of the Beta model
    alpha : float
        Power index of the beta model

    Attributes
    ----------
    sampler: instance child of _BaseSampler
        sampling of a unit circle centered in (0, 0)
    radius: float
        fiber radius
    area: float
        area of the fiber
    """

    def __init__(self, sampler, radius, amplitude, x_0, y_0, gamma, alpha,
                 **kwargs):
        super(MonteCarlo_Moffat2D, self).__init__(amplitude, x_0, y_0, gamma,
                                                  alpha, **kwargs)
        self.sampler = sampler
        self.radius = radius
        self.area = np.pi * radius**2
        self.fit_deriv = None

    def evaluate(self, x, y, amplitude, x_0, y_0, gamma, alpha):
        """
        Evaluate the model in *x* and *y* given the parameters.
        Integrates the Moffat with a Montecarlo like approach using the points
        from the sampler. Assumes that the sampler samples the correct radius

        Parameters
        ----------
        x, y: array-like or numeric value
            input coordinate values
        amplitude : float
            Amplitude of the model
        x_0 : float
            x position of the maximum of the Beta model
        y_0 : float
            y position of the maximum of the Beta model
        gamma : float
            Core width of the Beta model
        alpha : float
            Power index of the beta model

        Returns
        -------
        z: array-like or numeric value
            same type of the input *x* and *y* containing the integral of the
            Moffat distribution
        """
        moffat = super(MonteCarlo_Moffat2D, self).evaluate
        params = (amplitude, x_0, y_0, gamma, alpha)
        try:
            z = []
            for _x, _y in zip(x, y):
                xs, ys = self.sampler.get_samples(_x, _y, self.radius)
                _z = montecarlo_2d(moffat, xs, ys, self.area, *params)[0]
                z.append(_z)
            return np.array(z)
        except TypeError:  # x and y are not iterable
            xs, ys = self.sampler.get_samples(x, y, self.radius)
            return np.array(montecarlo_2d(moffat, xs, ys, self.area,
                                          *params)[0])


def montecarlo_2d(func, x, y, area, *args, **kwargs):
    """Compute the 2 dimensional integral of function *func* using a simple
    montecarlo-like integration.

    Parameters
    ----------
    func: callable
        2-dimensional function to evaluate: `f(x, y, *params)`
    x, y: of two arrays of size N or (2, N) array
        x and y coordinates of the points to use to compute the integral
    area: float
        area sampled by (`x`, `y`)
    args: list
        parameters to pass to the function
    kwargs: dictionary
        keyword parameter to pass to the function

    Returns
    -------
    I: float
        integral
    sI: float
        error on the integral
    """
    f_xy = func(x, y, *args, **kwargs)
    # evaluate the integral and its error
    I = area * f_xy.mean()
    sI = area * f_xy.std(ddof=1) / np.sqrt(x.size)
    return I, sI


# Initialise the sampler, the moffat, reconstruct the IFU head and select the
# fibers for the fit
def fit_image_quality(dither_file, ifucen_file, stars=None, fe_prefix='',
                      fextract=None, wmin=None, wmax=None, Sampler=GridSampler,
                      n_points=10000):
    """Fit the image quality on the reconstructed IFU defined by the dither and
    IFU center files.

    Parameters
    ----------
    dither_file: string
        name of the file defining the relative dither position, illumination
        and image quality
    ifucen_file: string
        name of the file with the position and throughput of the fibers on the
        IFU head
    stars: none or list of 2-tuples, optional
        If none, auto-detect stars on the reconstructed IFU (not implemented).
        Otherwise must be a list of (x, y) positions of stars on the IFU head
        to use for the fit
    fextract: None or list of fits files, optional
        if the name of the files to use for the reconstruction is not the same
        as the basenames in the dither file
    fe_prefix: string, optional
        when getting the names from the dither file, prepend *fe_prefix* to
        the *basename*
    wmin, wmax: float, optional
        min and max wavelength to use when doing the reconstruction. If *None*:
        use the min and/or max from the file
    Sampler: :class:`~_BaseSampler` child instance, optional
        type of sampler to use
    n_points: int, optional
        number of points to created in the sampler

    Returns
    -------
    best_fits: list of numpy arrays
        best fit parameters from the moffat, plus FWHM. One list entry of each
        of the fitted stars in the IFU head
        ``[np.array(amplitude, x_0, y_0, gamma, alpha, FWHM),]``

    Raises
    ------
    NotImplementedError
        if ``stars`` is ``None``


    ..todo:: 
        do we need to autodetect stars?

        this implementation is temporary or a very high level function. Need to
        atomise more to give more flexibility
    """
    # reconstruct the IFU head
    ifu = precon.ReconstructedIFU.from_files(ifucen_file, dither_file,
                                             fe_prefix=fe_prefix,
                                             fextract=fextract)
    xifu, yifu, fluxifu = ifu.reconstruct(wmin=wmin, wmax=wmax)
    # Autodetect (not yet)
    if stars is None:
        raise NotImplementedError("The autodetection is not yet implemented")

    sampler = Sampler(n_points)

    # TODO: is alpha=gamma=1 good enough?
    # initialise the model. Amplitude, x_0 and y_0 are set to 1, 0, 0 and
    # modified in the loop
    model = MonteCarlo_Moffat2D(sampler, ifu.ifu_center.fiber_d, 1, 0, 0, 1, 1)

    best_fits = []
    # loop through the stars
    for xstar, ystar in stars:
        # select only the fibers in 10" around the start
        # TODO: is 10 fine or need to be varied somehow?
        selected = (xifu - xstar)**2 + (yifu - ystar)**2 < 10.
        xi, yi, fluxi = xifu[selected], yifu[selected], fluxifu[selected]

        # updated the model
        model.amplitude = fluxi.max()
        model.x_0 = xstar
        model.y_0 = ystar

        # initialise the fitter
        fitter = apf.LevMarLSQFitter()
        # do the fit
        best_fit = fitter(model, xi, yi, fluxi)
        # get the params, flatten and add the FWHM
        params = best_fit.param_sets.flatten()
        params = np.append(params, get_fwhm(best_fit.gamma.value,
                                            best_fit.alpha.value))

        best_fits.append(params)

    return best_fits
