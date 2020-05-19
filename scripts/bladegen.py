import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

import utils as utils


class BladeGen:

    def __init__(self):
        self.npts = 118
        self.x = .5 * (1 - np.cos(np.linspace(0, np.pi, self.npts)))  # x-coord generation
        self.ds = pd.DataFrame(self.params(), index=[0])
        self.beta = [np.deg2rad(53), 0, 0, 0]
        self.beta[1] = utils.sdr(self.beta[0], self.ds.sigma_s, self.ds.df1)
        self.beta[2] = self.beta[1]
        self.beta[3] = utils.sdr(self.beta[2], self.ds.sigma_s, self.ds.df2)

        # single blade
        theta,lambd = utils.naca65gen(self.beta[0], self.beta[3], self.ds.sigma_s, self.ds.rth_s)
        self.ythickness(theta, self.ds.c_s[0])

    def params(self):
        """
        Generate parameters.
        :return:
        :param ds: dict with parameters
        """
        ds = {}
        ds['c_s'] = .43  # length of chord single
        ds['c_t'] = ds['c_s'] / 2  # length of chord tandem
        ds['th'] = .1 * ds['c_t']  # rel. thickness (identical for single and tandem)

        # Lieblein Diffusion Factor for front and rear blade
        ds['df1'] = .39
        ds['df2'] = .4915

        # division radius
        ds['sc_s'] = .43
        ds['sc_t'] = 1.16
        # compute division
        ds['s_s'] = ds['sc_s'] * ds['c_s']
        ds['s_t'] = ds['sc_t'] * ds['c_t']

        # real division: division and solicity
        # ds['s'] = 2 * np.pi * ds['r'] / ds['N_s']  # division
        ds['sigma_s'] = ds['c_s'] / ds['s_s']  # solicity s
        ds['sigma_t'] = ds['c_t'] / ds['s_t']  # solicity t

        # relative thickness
        ds['rth_s'] = ds['th'] / ds['c_s']
        ds['rth_t'] = ds['th'] / ds['c_t']
        return ds

    def ythickness(self, theta, c):
        ds = self.ds
        x = self.x
        yth = ds.th[0] * (1 - x) * (1.0675 * np.sqrt(x) - x * (.2756 - x * (2.4478 - 2.8385 * x))) / (
                1 - .176 * x)  # thickness distribution

        # calc circular arc camberline
        rc = c/2 * np.arcsin(theta/2) # radius of
        # yc = -rc * np.cos(theta/2)
        pts = np.linspace(0, np.pi, self.npts) # angles for 1/2 circle
        xc = yc = np.zeros(self.npts)
        xc = rc * np.cos(pts) + rc # x coords + offset r
        yc = rc * np.sin(pts) #

        0


if __name__ == "__main__":
    BladeGen()
