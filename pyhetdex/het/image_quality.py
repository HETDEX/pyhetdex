'''A server that supplies the image quality on the focal plane, as a function
of focal plane position.

Created on Aug 1, 2012

.. moduleauthor:: Daniel Farrow <dfarrow@mpe.mpg.de>

'''
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from abc import ABCMeta, abstractmethod
import numpy as np
import pyhetdex.het.image_quality

class _FwhmModel(object):
    """
    Abstract class that defines the methods of
    a model of the FWHM over the focal plane 
    """ 
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, gp_fhwm, gp_x, gp_y): 
        """ Initialize the model
         
        Parameters
        ----------
        gp_fwhm : float
            FWHM in the guide probe
        gp_x, gp_y : float
            x and y positon of the guide probe
            in arcseconds
        """
        pass

    @abstractmethod
    def fwhm(self, x, y):
        """ Returns the FWHM at x, y

        Parameters
        ----------
        x, y : float
            position in focal plane (relative
            to centre) in arcseconds         
        """
        pass



class _PowerLawModel(_FwhmModel):
    """
    A simple power law model of the FHWM variations
    over the focal fplane

    Attributes
    ----------
    R2 : float
        radius of focal plane in arcsec^2
    cen_fwhm : float
        FWHM at the center of the focal plane
    alpha : float
        Power law slope of change of FWHM with fplane position
    rs : float
        Scale length of powerlaw increase of FWHM

    """

    def __init__(self, gp_fwhm, gp_x, gp_y):
        
        self.R2 = 435600.0
        self.alpha = 2.0/3.0
        self.rs = 10.0
        self.cen_fwhm = cen_fwhm_from_gp(gp_fwhm, gp_x, gp_y)


    def cen_fwhm_from_gp(self, gp_fwhm, gp_x, gp_y):

        s_sq = (gp_x*gp_x + gp_y*gp_y)/(self.R2)
        return gp_fwhm - np.power((s_sq/self.rs), self.alpha) 

   
    def fwhm(self, x, y):
       
        s_sq = (x*x + y*y)/(self.R2)
        fwhm = (self.cen_fwhm + np.power((s_sq/self.rs), self.alpha))

        return fwhm

class _ConstantModel(_FwhmModel):
    """
    A simple FWHM model that is
    the same across the focal plane

    Attributes
    ----------
    fwhm : float
         FWHM in the focal plane
    """

    def __init__(self, gp_fwhm, gp_x, gp_y):
        
        self.cfwhm = gp_fwhm


    def fwhm(self, x, y):
        return self.cfwhm



class ImageQualityServer(object):
    """Image quality server

    Attributes
    ----------
    model : implementation of `class:` _FwhmModel 
        the model of the FHWM in the focal plane
    """

    def __init__(self, gp_fwhm, gp_x, gp_y, model='_ConstantModel'):
        """
        
        Parameters
        ----------
        gp_fwhm : float
            FWHM in the guide probe
        gp_x, gp_y : float
            x and y positon of the guide probe
            in arcseconds
        model : str 
            name of an implementation of the _FwhmModel
            class
        """ 

        self.model = (getattr(pyhetdex.het.image_quality, 
                              model))(gp_fwhm, gp_x, gp_y)   


    def fwhm(self, x, y):
        """
        Parameters
        ----------
        x, y : float
            position in the focal plane

        Returns
        -------
        fwhm : float
            fwhm at the position ``(x, y)``
        -----
        """

        return self.model.fwhm(x, y)











    

   
 
