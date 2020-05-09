import pandas as pd
import numpy as np
import scipy.optimize as optimize
from param import Param
import tools


class BladeGen:
    """
    2D Blade shape generation class.
    """

    def __init__(self):
        self.numpts = 300
        self.df_param = Param().df_params
        self.beta = self.redir_tandem()
        self.theta, self.lambd = tools.naca65gen(self.beta['beta11'], self.beta['beta12'], self.df_param.sigma_t.item(),
                                                 self.df_param.rth_t.item())
        self.parabolic_camber()

        0

    def redir_tandem(self):
        # ALL VALUES HAVE BEEN CHANGED TO RAD
        ds = self.df_param
        beta11 = np.deg2rad(53)
        beta12 = tools.sdr(beta11, ds['sigma_t'][0], ds['df1'][0])
        beta21 = beta12
        beta22 = tools.sdr(beta21, ds['sigma_t'][0], ds['df2'][0])
        df_t = (1 - (np.cos(beta11) / np.cos(beta22))) \
               + (np.cos(beta11) * (np.tan(beta11) - np.tan(beta22)) / (2 * (ds['c_s'][0] / ds['s_t'][0])))

        # dehaller over area ratio
        dehaller = np.cos(beta11) / np.cos(beta22)
        dehaller_fv = np.cos(beta11) / np.cos(beta12)
        dehaller_av = np.cos(beta12) / np.cos(beta22)

        # gather betas in a list
        beta = {'beta11': beta11,
                'beta12': beta12[0],
                'beta21': beta21[0],
                'beta22': beta22[0]}

        return beta

    def parabolic_camber(self):
        ds = self.df_param
        lambd = self.lambd
        theta = self.theta
        numpts = self.numpts
        a = ds.a_t1.item()
        # define points along the chord
        xchord = .5 * (1 - np.cos(np.linspace(0, np.pi, numpts)))

        # center of trailing edge radius
        xtec = 1 - ds.rTE_t.item()

        # Y-coord. of mean camber line (Skelettlinie)
        c = 1

        # compute b based on camber angle
        b = c * (np.sqrt(1 + (((4 * np.tan(theta)) ** 2) * ((a / c) - (a / c) ** 2 - 3 / 16))) - 1) / (
                    4 * np.tan(theta))

        # generate ycamber points
        ycamber = np.zeros(xchord.size)
        for i in range(0, xchord.size):
            x = xchord[i]
            y0 = 0
            fun = lambda y: (-y + x * (c - x) / (
            (((c - 2 * a) ** 2 / (4 * b ** 2)) * y + ((c - 2 * a) / b) * x - ((c ** 2 - 4 * a * c) / (4 * b)))))
            ycamber[i] = optimize.fsolve(fun, y0)

        camber = np.zeros((xchord.size, 2))
        camber[:, 0] = xchord
        camber[:, 1] = ycamber

        # blade inlet & outlet angle
        bia = np.arctan(4*b) / (4*a-c)
        boa = np.arctan(4*b) / (3*c-4*a)
        # tangent angle of skeletal line
        chicamber = np.tan(np.gradient(camber[:, 1]))/np.gradient(camber[:, 0]) #TODO: small divergence (+-1deg) from original script

        0


if __name__ == "__main__":
    BladeGen()
