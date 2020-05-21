import numpy as np
from matplotlib import pyplot as plt
from sklearn import preprocessing
import pandas as pd
import scipy.optimize as optimize

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
        theta, lambd = utils.naca65gen(self.beta[0], self.beta[3], self.ds.sigma_s, self.ds.rth_s)
        self.ythickness(lambd, theta, self.ds.c_s[0])

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

    def ythickness(self, lambd, theta, c):
        theta = np.deg2rad(55.0121)
        lambd = np.deg2rad(23.4077)
        c=1
        ds = self.ds
        # make a non linear x scaling for moving the extremum
        xcambermax = .4
        x = np.zeros(self.npts)
        half = int(np.round(self.npts/2))
        x[:half] = np.linspace(0, xcambermax, half)
        x[half-1:] = np.linspace(xcambermax, 1, half+1)
        x=x
        yth = ds.th[0] * (1 - x) * (1.0675 * np.sqrt(x) - x * (.2756 - x * (2.4478 - 2.8385 * x))) / (
                1 - .176 * x)  # thickness distribution

        # scale thickness
        foo = np.zeros((self.npts, 2))
        # foo[:, 0] = np.linspace(0, 1, self.npts)
        foo[:, 0] = x
        foo[:, 1] = yth
        min_max_scaler = preprocessing.MinMaxScaler()
        xy_th = min_max_scaler.fit_transform(foo)
        xy_th[:, 1] = xy_th[:, 1] * ds.th[0]


        # calc circular arc camberline (R. Aungier, p.65)
        rc = c / 2 * np.arcsin(theta / 2)  # radius of circular arc
        chalf = rc * np.sin(theta / 2)
        yc = -rc * np.cos(theta / 2)

        # origin @ (0, yc)
        pts = np.linspace(-chalf, chalf, self.npts)
        xy_camber = np.transpose(np.array([x, yc + np.sqrt(rc ** 2 - pts ** 2)]))
        xy_camber[:, 1] = xy_camber[:, 1]/np.linalg.norm(xy_camber[:, 1])

        # # FIXME: test with camber from matlab script
        # a = ds.c_s
        # c = 1
        # b = c * (np.sqrt(1 + (((4 * np.tan(theta)) ** 2) * ((a / c) - (a / c) ** 2 - 3 / 16))) - 1) / (
        #         4 * np.tan(theta))
        # ycambertemp = np.zeros(x.size)
        # for i in range(0, x.size):
        #     xtemp = x[i]
        #     y0 = 0
        #     fun = lambda y: (-y + xtemp * (c - xtemp) / (
        #             (((c - 2 * a) ** 2) / (4 * b ** 2)) * y + ((c - 2 * a) / b) * xtemp - (
        #             (c ** 2 - 4 * a * c) / (4 * b))))
        #     y = optimize.fsolve(fun, y0)
        #     ycambertemp[i] = y
        #
        # xy_camber = np.transpose(np.array([x, ycambertemp]))

        # xy surface
        yth_abs = np.abs(xy_th[:, 1])
        xsurface = np.zeros(2 * x.size - 1)
        ysurface = np.zeros(2 * x.size - 1)
        xss = x - yth_abs
        xps = x + yth_abs
        xsurface[:xss.size] = xps[::-1]
        xsurface[xss.size:] = xss[1:]

        yss = xy_camber[:, 1] + yth_abs
        yps = xy_camber[:, 1] - yth_abs
        ysurface[:yss.size] = yps[::-1]
        ysurface[yss.size:] = yss[1:]

        # Scale and rotate
        # scale with c
        xsurface = xsurface * c
        ysurface = ysurface * c

        X = np.cos(lambd) * xsurface - np.sin(lambd) * ysurface
        Y = np.sin(lambd) * xsurface + np.cos(lambd) * ysurface
        Xchord = (np.cos(lambd) * x - np.sin(lambd) * xy_camber[:, 1]) * c
        Ycamber = (np.sin(lambd) * x + np.cos(lambd) * xy_camber[:, 1]) * c

        plt.figure(2)
        plt.subplot(231)
        plt.plot(x, xy_th[:, 1])
        plt.subplot(232)
        plt.plot(x, xy_camber[:, 1])
        plt.subplot(233)
        plt.plot(Xchord, Ycamber)
        plt.subplot(234)
        plt.plot(xsurface, ysurface)
        plt.subplot(235)
        plt.plot(X, Y)
        plt.show()

        0


if __name__ == "__main__":
    BladeGen()
