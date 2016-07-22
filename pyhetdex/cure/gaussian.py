from __future__ import print_function

import numpy as np


class gauss1D_H(object):

    def __init__(self, powerlaw_wings):
        self.powerlaw_wings = powerlaw_wings

    def _powerlaw_wings(self, x):
        return 1.0 / (self.powerlaw_wings[1] + self.powerlaw_wings[2]
                      * np.power(abs(x), self.powerlaw_wings[3]))

    def eval(self, x, amp, x0, sig, H2, H3, ex):
        n1 = (1.0 + H2 * 3.0 / np.sqrt(24.))
        z1 = (x - x0) / sig
        z2 = np.power(abs(z1), ex)
        e1 = np.exp(-0.5 * z2)
        h3_1 = 1. / np.sqrt(6.) * (2. * np.sqrt(2.)
                                   * z1*z1*z1 - 3. * np.sqrt(2.) * z1)
        h4_1 = 1. / np.sqrt(24.) * (4. * z1*z1*z1*z1 - 12. * z1*z1 + 3.)

        return amp/n1*e1*(1.0+H2*h4_1+H3*h3_1) + self.powerlaw_wings[0]/n1 * amp \
            * self._powerlaw_wings(x-x0)
