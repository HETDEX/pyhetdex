"""
Module to store luminosity functions. Useful for assigning
fluxes to random points.

AUTHOR(S): Daniel Farrow 2016

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from abc import ABCMeta, abstractmethod
from numpy import cumsum, interp, arange, ones

class LuminosityFunction( object ):
    """
    Abstract class to define an interface to
    luminosity function objects

    Parameters
    ----------
    lmin, lmax : float
        the minimum and maximum range of 
        luminosity (for the cumulative LF)
    nbins : optional
        the number of bins for calculating
        the cumulative LF numerically

    """

    __metaclass__ = ABCMeta

    @abstractmethod 
    def __init__(self, lmin, lmax, nbins, *args, **kwargs):

        self.nbins = nbins # Number of bins for cached CLF
        self.lmin = lmin # Minimum luminosity
        self.lmax = lmax # Maximum luminosity
        self.cuma = None # Array to store cached CLF
        self.stepsize = (self.lmax - self.lmin)/self.nbins  
        self.l_c = arange(self.lmin, self.lmax, self.stepsize)

    @abstractmethod
    def __call__(self, l):
        pass

    def _cache_normed_cumulative(self):
        """ 
        Calculate and store the 
        cumulative luminosity function,
        normalized (i.e. goes from 0 to 1
        as L increases)
        """
        self.cuma = cumsum(self.__call__(self.l_c))
        self.cuma = self.cuma/self.cuma[-1]

    def normed_cumulative(self, l):
        """
        Return the normalized, cumulative
        luminosity function at luminosity l. Uses
        a cached, numerically intergrated version of
        the luminosity function.

        Parameters
        ----------
        l : float
            the luminosity
        """
        if self.cuma is not None:
            return interp(l, self.l_c, self.cuma)
        else:
           self._cache_normed_cumulative() 
           return interp(l, self.l_c, self.cuma)

    def inverse_normed_cumulative(self, n):
        """
        Return the inverse of the normalized, cumulative
        luminosity function at luminosity l. Uses
        a cached, numerically intergrated version of
        the luminosity function.

        Parameters
        ----------
        n : float
            a value between 0 and 1
        """

        if self.cuma is not None:
            return interp(n, self.cuma, self.l_c)
        else:
           self._cache_normed_cumulative() 
           return interp(n, self.cuma, self.l_c)

 


class FlatLuminosityFunction( LuminosityFunction ):
      """
      A flat luminosity function between two 
      L limits. 

      Parameter
      ---------
      lmin, lmax : float
          the minimum and maximum luminosities for
          the LF

      """

      def __init__(self, lmin, lmax, nbins=200, **kwargs):

          LuminosityFunction.__init__(self, lmin, lmax, nbins, **kwargs)

      def __call__(self, l):

          return ones(len(l))







     


 


