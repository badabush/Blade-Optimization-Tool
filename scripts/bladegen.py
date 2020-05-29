import numpy as np
from matplotlib import pyplot as plt
from sklearn import preprocessing
import pandas as pd
import scipy.optimize as optimize
import scripts.bladetools as utils


class BladeGen:

    def __init__(self, nblade='single', r_th=.0215, beta1=30, beta2=30, x_maxcamber=.4, l_chord=1.0, lambd=0,
                 rth_le=0.01, rth_te=0.0135, npts=500):

        # assert input
        self.assert_input(nblade, r_th, beta1, beta2, x_maxcamber, rth_le, rth_te, npts)

        self.npts = npts
        self.x = .5 * (1 - np.cos(np.linspace(0, np.pi, self.npts)))  # x-coord generation
        self.rth = r_th  # rel. thickness
        self.nblade = nblade
        self.c = l_chord
        self.th_le = rth_le / self.c  # rth leading edge
        self.th_te = rth_te / self.c  # rth trailing edge

        # pack dict into pandas frame
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
        Return dataset (ds) with parameters.

        :return: ds
        :rtype ds: dict
        """
        ds = {}
        ds['c_s'] = .43  # length of chord single
        ds['c_t'] = ds['c_s'] / 2  # length of chord tandem
        ds['th'] = self.rth
        ds['r_te'] = self.th_te

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
        Returns  vector with X and Y of thickness distribution.

        :return: xy_th
        :rtype xy_th: (npts, 2) ndarray
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
        Returns vector with X and Y of camber line.

        :param theta: sum of beta1 and beta2 (Chi1 and Chi2 in R.Aungier)
        :type theta: float
        :param a: max. chamber position
        :type a: float
        :return: xy_camber
        :rtype xy_camber: (npts, 2) ndarray
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
        Returns vector with X and Y of blade geometry.

        :param lambd: Rotation of blade
        :type lambd: float
        :param c: chord length
        :type c: float
        :param xy_th: X and Y points from method thickness_dist
        :type xy_th: (npts, 2) float-array
        :param xy_camber: X and Y points from method camberline
        :type xy_camber: (npts, 2) float-array
        :return: xy_blade
        :rtype xy_blade: (npts, 2) float-array
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

        # Leading edge radius fitting
        if self.th_le>0:
            xsurface, ysurface = utils.rte_fitter('LE', xsurface, ysurface, self.th_le / 2, xy_camber)

        # Trailing edge radius fitting
        if self.th_te>0:
            xsurface, ysurface = utils.rte_fitter('TE', xsurface, ysurface, self.th_te / 2, xy_camber)

        X = np.cos(lambd) * xsurface - np.sin(lambd) * ysurface
        Y = np.sin(lambd) * xsurface + np.cos(lambd) * ysurface
        xy_blade = np.transpose(np.array([X, Y]))

        return xy_blade

    def assert_input(self, nblade, r_th, beta1, beta2, x_maxcamber, rth_le, rth_te, npts):
        """
        Assert input parameter are within defined range.

        :param nblade: number of blades, default: 'single'
        :type nblade: str
        :param r_th: relative thickness, default: .0215
        :type r_th: float
        :param beta1: inlet angle, default: 25
        :type beta1: float
        :param beta2: outlet angle, default: 25
        :type beta2: float
        :param x_maxcamber: X position of max. chamber, default: .4
        :type x_maxcamber: float
        :param rth_le: rel. thickness leading edge as percentage of chord, default: .02
        :type rth_le: float
        :param rth_te: rel. thickness trailing edge as percentage of chord, default: .0135
        :type rth_te: float
        :param npts: number of blade points, default: 400
        :type npts: int
        :raises: Assertion Errors
        """
        # Either single or tandem
        assert ((nblade == 'single') or (nblade == 'tandem')), "single or tandem"

        # Blade arc flips above sum(beta1,beta2)>90
        assert ((rth_le < r_th * 2) and (rth_le >= 0)), "rth_le out of range"
        assert ((rth_te < r_th * .75) and (rth_te >= 0)), "rth_te out of range"

        assert ((x_maxcamber > 0) and (x_maxcamber < 1)), "x max chamber out of range [0,1]."
        # LE/TE Radius doesnt work properly outside of range
        assert ((beta1 + beta2) <= 90), "Beta1 + Beta2 must be smaller than 90"

        # Blade looks absolute horrible sub 200 points..
        assert (npts >= 200), "Choose more than 200 Pts"

    def get_points(self, xy):
        0

    def debug_plot(self, xy_th, xy_camber, xy_blade):
        plt.figure(figsize=(12, 4))
        # plt.subplot(131)
        # plt.plot(self.x, xy_th[:, 1])
        # plt.subplot(132)
        # plt.plot(self.x, xy_camber[:, 1])
        # plt.subplot(133)
        plt.plot(xy_blade[:, 0], xy_blade[:, 1])
        plt.axis('equal')
        plt.show()


if __name__ == "__main__":
    BladeGen()
