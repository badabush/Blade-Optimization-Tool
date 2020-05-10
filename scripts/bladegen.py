import pandas as pd
import numpy as np
import scipy.optimize as optimize
from matplotlib import pyplot as plt
from param import Param
import tools


class BladeGen:
    """
    2D Blade shape generation class.
    """

    def __init__(self):
        """
        Some very inspirational comments.

        """
        self.npoints = 300
        self.df_param = Param().df_params  # get parameters from param.py
        self.beta = self.redir_tandem()
        self.frontblade = self.blade_shaper(self.beta['beta11'], self.beta['beta12'], self.df_param.a_t1.item(),
                                            self.df_param.gammahk_t1.item())
        self.rearblade = self.blade_shaper(self.beta['beta21'], self.beta['beta22'], self.df_param.a_t2.item(),
                                            self.df_param.gammahk_t2.item())

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

    def parabolic_camber(self, lambd, theta, a_t, gammahk):
        ds = self.df_param
        numpts = self.npoints
        a = a_t
        # define points along the chord
        x1chord = .5 * (1 - np.cos(np.linspace(0, np.pi, numpts)))

        # center of trailing edge radius
        xtec = 1 - ds.rTE_t.item()

        # Y-coord. of mean camber line (Skelettlinie)
        c = 1

        # compute b based on camber angle
        b = c * (np.sqrt(1 + (((4 * np.tan(theta)) ** 2) * ((a / c) - (a / c) ** 2 - 3 / 16))) - 1) / (
                4 * np.tan(theta))

        # generate y1camber points
        y1camber = np.zeros(x1chord.size)
        for i in range(0, x1chord.size):
            x = x1chord[i]
            y0 = 0
            fun = lambda y: (-y + x * (c - x) / (
                (((c - 2 * a) ** 2 / (4 * b ** 2)) * y + ((c - 2 * a) / b) * x - ((c ** 2 - 4 * a * c) / (4 * b)))))
            y1camber[i] = optimize.fsolve(fun, y0)

        camber = np.zeros((x1chord.size, 2))
        camber[:, 0] = x1chord
        camber[:, 1] = y1camber

        # blade inlet & outlet angle
        bia = np.arctan(4 * b) / (4 * a - c)
        boa = np.arctan(4 * b) / (3 * c - 4 * a)
        # tangent angle of skeletal line
        chicamber = np.tan(np.gradient(camber[:, 1])) / np.gradient(
            camber[:, 0])  # TODO: small divergence (+-1deg) from original script
        camber2 = np.zeros((x1chord.size, 2))  # FIXME: this is called woelbung in the original .m
        camber2[:, 0] = x1chord
        camber2[:, 1] = chicamber

        # rotating x1chord and y1camber
        xrot = np.cos(lambd) * x1chord - np.sin(lambd) * y1camber
        yrot = np.sin(lambd) * x1chord + np.cos(lambd) * y1camber
        x2chord = xrot
        y2camber = yrot

        # length of mean camber line
        meancamber = np.zeros(self.npoints)
        meancamber[1:] = np.cumsum(np.sqrt(np.diff(x1chord) * np.diff(x1chord) + np.diff(y1camber) * np.diff(y1camber)))
        meancamber = meancamber / meancamber[-1]

        # parametric thickness dist from henners studies (?)
        rn = 4 * ds.rLE_t.item()
        dhk = 2 * ds.rTE_t.item()
        d = ds.rth_t.item()
        xd = ds.xd.item()

        ## LEADING EDGE
        x1chord_short = x1chord[np.where(x1chord < (1 - ds.rTE_t.item()))]
        x1chord_front = x1chord_short[np.where(x1chord_short < ds.xd.item())]
        # FIXME: autoformat long formula issue
        y1thick_front = .5 * (np.sqrt(2 * rn) * np.sqrt(x1chord_front) +
                              (((3 * d) / xd) - (15 / 8) * np.sqrt(2 * rn / xd) - (3 * xd * (d - dhk)) / (
                                      (c - xd) ** 2) + (
                                       2 * xd * np.tan((gammahk) / 2)) / (c - xd)) * x1chord_front
                              + ((5 / 4) * np.sqrt((2 * rn) / (xd ** 3)) - (3 * d) / (xd ** 2) - (
                        4 * np.tan(gammahk / 2)) / (c - xd) + (6 * (d - dhk)) / ((
                                                                                         c - xd) ** 2)) * x1chord_front ** 2
                              + ((2 * np.tan(gammahk / 2)) / (xd * (c - xd)) - (3 * (d - dhk)) / (
                        xd * (c - xd) ** 2) -
                                 (3 / 8) * np.sqrt((2 * rn) / (xd ** 5)) + d / (xd ** 3)) * x1chord_front ** 3)

        x1chord_back = x1chord_short[np.where(x1chord_short >= xd)]
        y1thick_back = .5 * (dhk + (2 * np.tan(gammahk / 2)) * (c - x1chord_back)
                             + (((3 * (d - dhk)) / (c - xd) ** 2) - (4 * np.tan(gammahk / 2)) / (
                        c - xd)) * (
                                     c - x1chord_back) ** 2
                             + (((2 * np.tan(gammahk / 2)) / (c - xd) ** 2) - (
                        (2 * (d - dhk)) / (c - xd) ** 3)) * (c - x1chord_back) ** 3)

        # concatenate front and back parts of ythick
        ythicknaca65 = np.concatenate((y1thick_front, y1thick_back))

        ## TRAILING EDGE
        rte1 = ythicknaca65[-1]
        y1thick_circte = np.zeros(300)  # initialize array
        y1thick_circte = np.where(x1chord > (1 - ds.rTE_t.item()),
                                  np.sqrt(rte1 ** 2 - (x1chord - (1 - rte1)) ** 2), np.nan)
        y1thick_circte = y1thick_circte[~np.isnan(y1thick_circte)]  # omit nans
        y1thick = np.concatenate((np.abs(ythicknaca65), np.abs(y1thick_circte)))

        thick_dist = np.zeros((y1thick.size, 2))
        thick_dist[:, 0] = y1thick
        thick_dist[:, 1] = x1chord

        # overlapping mean camber line and thickness distribution
        x_ss = x1chord - np.sin(chicamber) * y1thick
        x_ps = x1chord + np.sin(chicamber) * y1thick
        y_ss = y1camber + np.cos(chicamber) * y1thick
        y_ps = y1camber - np.cos(chicamber) * y1thick

        # concat flipped ps with ss
        x = np.concatenate((x_ps[::-1], x_ss[1:-1]))
        y = np.concatenate((y_ps[::-1], y_ss[1:-1]))

        ## scale and rotate
        chord = ds.c_t.item()

        # scale
        x = x * chord
        y = y * chord

        # rotate
        xrot = np.cos(lambd) * x - np.sin(lambd) * y
        yrot = np.sin(lambd) * x + np.cos(lambd) * y
        x = xrot
        y = yrot

        x2rot = np.cos(lambd) * x1chord - np.sin(lambd) * y1camber
        y2rot = np.sin(lambd) * x1chord + np.cos(lambd) * y1camber

        x2chord = x2rot * chord
        y2camber = y2rot * chord

        camber = np.zeros((x1chord.size, 2))
        camber[:, 0] = x2chord
        camber[:, 1] = y2camber

        return x, y, camber, camber2, thick_dist, bia, boa

    def blade_shaper(self, beta1, beta2, at, gammahk):
        theta, lambd = tools.naca65gen(beta1, beta2, self.df_param.sigma_t.item(),
                                       self.df_param.rth_t.item())
        x, y, camber, thick_dist, camber2, bia, boa = self.parabolic_camber(lambd, theta, at, gammahk)
        c_ax1 = np.cos(lambd) * self.df_param.c_t.item()
        bia = bia + lambd
        boa = lambd - boa

        # stuff parameters into a dict
        bladeparms = {'x': x, 'y': y, 'bia': bia, 'boa': boa, 'camber': camber, 'thick_dist': thick_dist, 'camber2': camber2}

        return bladeparms


if __name__ == "__main__":
    BladeGen()
