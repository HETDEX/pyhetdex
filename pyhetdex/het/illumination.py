"""Illumination server

Returns the illumination in the focal plane of HE for a focal
plane position and a tracker position

.. moduleauthor:: Daniel Farrow <dfarrow@mpe.mpg.de>
"""

from __future__ import absolute_import, print_function

import numpy as np


class IlluminationServer(object):
    """Illumination server.

    At the moment returns a dummy model for how the illumnation
    varies across the focal plane
    """

    def __init__(self, tracker_position, illumination_model="Constant"):
        """
        Parameters
        ----------
        illumination_model : string
            name of the illumination model to use
        self.tracker_position : list of lists ??
            the position of the tracker for the different 
            dithers
        """ 

        self.tracker_position = tracker_position

        # Specify throughput model
        self.illumination_model = illumination_model



    def illumination(self, x, y):
        """Throughput based on focal plane position.

        Now is just a dummy model.

        Parameters
        ----------
        x, y : float
            focal plane position of the IFU in arcseconds

        Returns
        -------
        r : float
            illumination at the input position

        Raises
        ------
        NotImplementedError
            if the required illumination model is not implemented

        Notes
        -----
            This is also a dummy, should contain some clever model to give at
            the moment just falls off like a power law
        """

        if "Constant" in self.illumination_model:
            r = 1.0
        elif "SimplePowerLaw" in self.illumination_model:
            s_sq = (x*x + y*y)/(435600.0)
            r = 1.0 / (1.0 + s_sq)
        else:
            msg = "[IlluminationServer] Error: Unrecognised IlluminationModel"
            msg += "choice : {}".format(self.illumination_model)
            raise NotImplementedError(msg)

        return r
