""" Telescope module

Stores information related to the guide, i.e. guide probe and tracker
information. Also deals with illumination and image quality servers.

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyhetdex.het.illumination import IlluminationServer
from pyhetdex.het.image_quality import ImageQualityServer


class Shot(object):
    """ Class to store information about the
    whole shot, specifically tracker and
    guide-probe information

    Read in the list of dither positions as a function of IHMPID. Read in
    tracker info and guide probe data for each dither from files is `shot_dir`.
    Initialize the illumination and transparency servers.

    Parameters
    ----------
    shot_dir : str
        the directory of the shot
    """
    def __init__(self, shot_dir):
        # TODO .. read these from GP files
        # (expected flux / measured flux) in GP
        self.gp_normalisation = [1.0, 1.0, 1.0]
        # fhwm in the dithers
        self.gp_fwhm = [1.6, 1.6, 1.6]
        # positions of GPs in different dithers
        self.gp_x = [450.0, -450.0, -450.0]
        self.gp_y = [-450.0, -450.0, 450.0]

        # position of the tracker for the different
        # dithers (in some coordinate system)
        self.tracker_position = [[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]]

        # set up image quality and illumination model servers
        self.fwhm_servers = []
        self.illu_servers = []
        self.transparency = []

        for dither in range(3):
            self.fwhm_servers.append(ImageQualityServer(self.gp_fwhm[dither],
                                                        self.gp_x[dither],
                                                        self.gp_y[dither]))

            illumination = IlluminationServer(self.tracker_position[dither])
            self.illu_servers.append(illumination)

            # transparency is the normalisation of the GP after correcting for
            # illumination, divide normalisation by illumination at the guide
            # probe
            self.transparency.append(self.gp_normalisation[dither] /
                                     illumination.illumination(self.gp_x[dither],
                                                               self.gp_y[dither]))

    def fwhm(self, x, y, dither):
        """ Return the FWHM

        Parameters
        ----------
        x, y : float
            position in the focal plane in arcseconds
        dither : int
            the dither number (0 to 2)
        """
        return self.fwhm_servers[dither].fwhm(x, y)

    def illumination(self, x, y, dither):
        """ Return the illumination

        Parameters
        ----------
        x,y : float
            position in the focal plane in arcseconds
        dither : int
            the dither number (0 to 2)
        """
        return self.illu_servers[dither].illumination(x, y)

    def transparency(self, dither):
        """ Return the sky transparency

        Parameters
        ----------
        dither : int
            the dither number (0-2)
        """
        return self.transparency[dither]

    def normalisation(self, x, y, dither):
        """ Return the normalisation (transp*illu)

        Parameters
        ----------
        x, y : float
            position in the focal plane in arcseconds
        dither : int
            the dither number (0 to 2)
        """
        return (self.illu_servers[dither].illumination(x, y) *
                self.transparency[dither])
