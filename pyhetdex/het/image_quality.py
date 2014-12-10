'''
A server that supplies the image quality
on the focal plane, as a function of
fplane position. Pass a shot object that
contains important telescope information

Created on Aug 1, 2012

@author: dfarrow
'''

from __future__ import absolute_import, print_function
import numpy

class imageQualityServer:
  
    def __init__(self, gconfig, shot):
        
        self.R2 = 435600.0 #(radius of focal plane in arcsec)^2
        self.shot = shot
        self.gconfig = gconfig
        
        #FWHM at center of fplane
        self.cenFWHM = self.gconfig.getfloat("imageQualityServer", "fwhm_cen")
        
        #Power law slope of change of FWHM with fplane position
        self.alpha = 2.0/3.0

        # Scale length of powerlaw increase of FWHM
        self.rs = 10.0
        
  
    def fplaneToFWHM(self, x, y):
        # This is also a dummy, should contain some clever model to give FWHM based on focal 
        # plane position, at the moment just falls off like a power law
        s_sq = (x*x + y*y)/(self.R2) 
        fwhm = (self.cenFWHM + numpy.power((s_sq/self.rs), self.alpha)) 
        print("[imagequalityserver] Calculated FWHM to be %3.2f"%fwhm)
        
        return fwhm
        