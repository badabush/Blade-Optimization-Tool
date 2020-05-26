import numpy as np
from matplotlib import pyplot as plt
from sklearn import preprocessing
import pandas as pd
import scipy.optimize as optimize

import utils as utils


class BladeGen:

    def __init__(self, nblade='single', r_th=.0215, beta1=25, beta2=25, x_maxcamber=.4, l_chord=1, lambd=0, r_te=.004):
        self.npts = 400
        self.x = .5 * (1 - np.cos(np.linspace(0, np.pi, self.npts)))  # x-coord generation
        self.rth = r_th # rel. thickness
        self.rte = r_te # radius trailing edge
        self.ds = pd.DataFrame(self.params(), index=[0])

        self.beta = [beta1, beta2]
        theta = np.deg2rad(np.sum(self.beta))
        lambd = np.deg2rad(lambd)

        xy_th = self.thickness_dist()
        xy_camber = self.camberline(theta, x_maxcamber)
        xy_blade = self.geom_gen(xy_th, xy_camber, lambd, l_chord)
        self.get_points(xy_blade)
        self.debug_plot(xy_th, xy_camber, xy_blade)

    def params(self):
        """
        Generate parameters.
        :return:
        :param ds: dict with parameters
        """
        ds = {}
        ds['c_s'] = .43  # length of chord single
        ds['c_t'] = ds['c_s'] / 2  # length of chord tandem
        ds['th'] = self.rth
        ds['r_te'] = self.rte

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

    def thickness_dist(self):
        """
        Calculate thickness distribution.

        :return:
        :param xy_th: (npts, 2) vector with X and Y of thickness distribution
        """

        ds = self.ds
        x = self.x
        yth = ds.th[0] * (1 - x) * (1.0675 * np.sqrt(x) - x * (.2756 - x * (2.4478 - 2.8385 * x))) / (
                1 - .176 * x)  # thickness distribution

        # scale thickness
        th_noscale = np.zeros((self.npts, 2))
        th_noscale[:, 0] = x
        th_noscale[:, 1] = yth
        min_max_scaler = preprocessing.MinMaxScaler()
        xy_th = min_max_scaler.fit_transform(th_noscale)
        xy_th[:, 1] = xy_th[:, 1] * ds.th[0]

        return xy_th

    def camberline(self, theta, a):
        """
        Calculate the parabolic-arc camberline from R.Aungier.

        :param theta: sum of beta1 and beta2 (Chi1 and Chi2 in R.Aungier)
        :param a: max. chamber position
        :return:
        :param xy_camber: (npts, 2) vector with X and Y of camber line
        """

        x = self.x
        c = 1
        b = c * (np.sqrt(1 + (((4 * np.tan(theta)) ** 2) * ((a / c) - (a / c) ** 2 - 3 / 16))) - 1) / (
                4 * np.tan(theta))
        ycambertemp = np.zeros(x.size)
        for i in range(0, x.size):
            xtemp = x[i]
            y0 = 0
            fun = lambda y: (-y + xtemp * (c - xtemp) / (
                    (((c - 2 * a) ** 2) / (4 * b ** 2)) * y + ((c - 2 * a) / b) * xtemp - (
                    (c ** 2 - 4 * a * c) / (4 * b))))
            y = optimize.fsolve(fun, y0)
            ycambertemp[i] = y

        xy_camber = np.transpose(np.array([x, ycambertemp]))

        return xy_camber

    def geom_gen(self, xy_th, xy_camber, lambd, c):
        """
        Generate the Blade shape.

        :param lambd: Rotation of blade
        :param c: chord length
        :param xy_th: X and Y points from method thickness_dist
        :param xy_camber: X and Y points from method camberline
        :return:
        :param xy_blade: (npts, 2) vector with X and Y of blade geometry
        """

        x = self.x

        # xy surface
        yth_abs = np.abs(xy_th[:, 1])
        xsurface = np.zeros(2 * x.size)
        ysurface = np.zeros(2 * x.size)
        xss = x - yth_abs
        xps = x + yth_abs
        xsurface[:xss.size] = xps[::-1]
        xsurface[xss.size:] = xss[0:]

        yss = xy_camber[:, 1] + yth_abs
        yps = xy_camber[:, 1] - yth_abs
        ysurface[:yss.size] = yps[::-1]
        ysurface[yss.size:] = yss[0:]

        # Scale and rotate
        # scale with c
        xsurface = xsurface * c
        ysurface = ysurface * c
        utils.rte_fitter(xsurface, ysurface, self.rte, xy_camber)

        X = np.cos(lambd) * xsurface - np.sin(lambd) * ysurface
        Y = np.sin(lambd) * xsurface + np.cos(lambd) * ysurface
        # Xchord = (np.cos(lambd) * x - np.sin(lambd) * xy_camber[:, 1]) * c
        # Ycamber = (np.sin(lambd) * x + np.cos(lambd) * xy_camber[:, 1]) * c

        xy_blade = np.transpose(np.array([X, Y]))

        return xy_blade

    def get_points(self, xy):
        0

    def debug_plot(self, xy_th, xy_camber, xy_blade):
        plt.figure(figsize=(12, 4))
        plt.subplot(131)
        plt.plot(self.x, xy_th[:, 1])
        plt.subplot(132)
        plt.plot(self.x, xy_camber[:, 1])
        plt.subplot(133)
        plt.plot(xy_blade[:, 0], xy_blade[:, 1])
        plt.axis('equal')
        plt.show()
        0


if __name__ == "__main__":
    BladeGen()
