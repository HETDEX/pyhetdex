"""Illumination and throughput server

Returns the illumination & throughput in the focal plane of HE for a focal
plane position and a ``shot`` object containing important information about the
telescope configuration

.. moduleauthor:: Daniel Farrow <dfarrow@mpe.mpg.de>

.. todo::
    a module in :mod:`~pyhetdex` should not depend on the structure of a class
    defined in code that uses :mod:`~pyhetdex`. Here referring to ``shot``

    either pass the ``illumination_model`` option as parameters to
    :meth:`~ThroughputServer.fplaneToThroughput` or check that it is
    implemented when initialising :class:`~ThroughputServer`.
"""
from __future__ import absolute_import, print_function

import numpy as np


class ThroughputServer(object):
    """Throughput server.

    At the moment returns a dummy model for the throughput across the focal
    plane

    Parameters
    ----------
    throughput_file : string
    illumination_model : string
    shot : ??

    Attributes
    ----------
    name : string
        name of the server
    shot : ??
        ??
    throughput_file : string
        name of the throughput file
    lambdas, throughputs : nd-arrays
        throughput as function of wavelength
    illumination_model : string
        name of the illumination model to use
    """

    def __init__(self, throughput_file, illumination_model, shot):
        self.shot = shot
        # Read in throughput file
        self.throughput_file = throughput_file
        self.lambdas, self.throughputs = \
                self.loadThroughputTemplate(self.throughput_file)
        # Specify throughput model
        self.illumination_model = illumination_model

        self.name = "Dummy throughput server"

    def loadThroughputTemplate(self, throughput_file):
        """Load the throughput template

        Parameters
        ----------
        throughput_file : string
            name of the throughput file

        Returns
        -------
        lambdas, throughputs : nd arrays
            throughput as function of wavelength

        Raises
        ------
        IOError
            re-raise after printing an error message if the input file does not
            exists
        """

        lambdas = []
        throughputs = []

        try:
            with open(throughput_file) as f:
                for l in f:
                    if l.startswith("#"):
                        continue
                    lambdas.append(float(l.split()[0]))
                    throughputs.append(float(l.split()[1]))

            norm = max(throughputs)
            throughputs = np.array(throughputs) / norm
        except IOError:
            print("ERROR: Could not open ", throughput_file)
            raise

        return np.array(lambdas), throughputs

    def outputThroughputFile(self, ID, x, y,
                             fname_template="throughput{id:04d}.dat"):
        """Save throughput file.

        The template throughput is multiplied by a focal-plane position
        dependent illumination correction before saving it. This correction is
        returned

        Parameters
        ----------
        ID : int
            ID to replace into the output file name template
        x, y : float
            focal plane position of the IFU in arcseconds

        Returns
        -------
        f_illum : float
            focal plane position dependent illumination
        """

        outfile = fname_template.format(id=ID)

        f_illum = self.fplaneToThroughput(x, y)
        out_array = np.vstack([self.lambdas, self.throughputs * f_illum]).T

        np.savetxt(outfile, out_array, fmt='%5.2f', delimiter="\t",
                   header='# L throughput')

        return f_illum

    def fplaneToThroughput(self, x, y):
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

        if "SimplePowerLaw" in self.illumination_model:
            s_sq = (x*x + y*y)/(435600.0)
            r = 1.0 / (1.0 + s_sq)
        else:
            msg = "[throughputServer] Error: Unrecognised IlluminationModel"
            msg += "choice : {}".format(self.throughput_model)
            raise NotImplementedError(msg)

        return r
