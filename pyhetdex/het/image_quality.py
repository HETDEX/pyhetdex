'''A server that supplies the image quality on the focal plane, as a function
of focal plane position. Pass a ``shot`` object that contains important
telescope information

Created on Aug 1, 2012

.. moduleauthor:: Daniel Farrow <dfarrow@mpe.mpg.de>

.. todo::
    a module in :mod:`~pyhetdex` should not depend on the structure of a class
    defined in code that uses :mod:`~pyhetdex`. Here referring to ``shot``
'''

from __future__ import absolute_import, print_function

import numpy


class ImageQualityServer(object):
    """Image quality server

    Attributes
    ----------
    R2: float
        radius of focal plane in arcsec^2
    shot: ??
        ??
    cenFWHM: float
        FWHM at the center of the focal plane
    alpha: float
        Power law slope of change of FWHM with fplane position
    rs: float
        Scale length of powerlaw increase of FWHM

    Parameters
    ----------
    cenFWHM: float
    shot: ??
    """

    def __init__(self, cenFWHM, shot):
        self.R2 = 435600.0
        self.shot = shot
        self.cenFWHM = cenFWHM
        self.alpha = 2.0/3.0
        self.rs = 10.0

    def fplaneToFWHM(self, x, y):
        """Dummy image quality model that just falls off like a power law.

        Parameters
        ----------
        x, y: float
            position in the focal plane

        Returns
        -------
        fwhm: float
            fwhm at the position ``(x, y)``

        Note
        ----
            Should contain some clever model to give FWHM based on focal plane
            position
        """

        s_sq = (x*x + y*y)/(self.R2)
        fwhm = (self.cenFWHM + numpy.power((s_sq/self.rs), self.alpha))
        print("[imagequalityserver] Calculated FWHM to be %3.2f" % fwhm)

        return fwhm
