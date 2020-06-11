import numpy as np
from matplotlib import pyplot as plt
from sklearn import preprocessing
import pandas as pd
import scipy.optimize as optimize
from roundedges import RoundEdges
from bladetools import ImportExport, normalize


class BladeGen:

    def __init__(self, frontend='user', file='', nblade='single', th_dist_option=1, r_th=.0215, beta1=25, beta2=25,
                 x_maxcamber=.4,
                 x_maxth=.3, l_chord=1.0, lambd=20, rth_le=0.01, rth_te=0.0135, npts=1000):

        # assert input
        self.file = file
        if self.file != '':
            try:
                self.xy_in = ImportExport()._import(file)
                self.xy_in = normalize(self.xy_in)
            except (ImportError, AttributeError) as e:
                print(e)
        self.assert_input(nblade, r_th, beta1, beta2, x_maxcamber, rth_le, rth_te, npts)
        self.npts = int(npts / 2)
        self.x = .5 * (1 - np.cos(np.linspace(0, np.pi, self.npts)))  # x-coord generation
        self.rth = r_th*10  # rel. thickness #fixme: thickness does not work properly
        self.nblade = nblade
        self.c = l_chord
        self.th_le = rth_le * self.c  # rth leading edge
        self.th_te = rth_te * self.c  # rth trailing edge
        self.thdist_option = th_dist_option
        self.x_max_th = x_maxth

        # pack dict into pandas frame
        self.ds = pd.DataFrame(self.params(), index=[0])

        self.beta = [beta1, beta2]
        theta = np.deg2rad(np.sum(self.beta))
        self.lambd = np.deg2rad(lambd)

        self.xy_camber = self.camberline(theta, x_maxcamber)
        if self.thdist_option == 0:
            xy_th = self.thickness_dist_v1()
            xy_blade = self.geom_gen(xy_th, self.lambd, l_chord)
            xy_blade = normalize(xy_blade)
        elif self.thdist_option == 1:
            xy_blade = self.thickness_dist_v2()
        if frontend == 'user':
            ImportExport()._export(xy_blade)
            # self.debug_plot(xy_th, xy_camber, xy_blade)
        elif frontend == 'gui':
            self.xy_blade = xy_blade
            self._return()

    def params(self):
        """
        Generate parameters.
        Return dataset (ds) with parameters.

        :return: ds
        :rtype ds: dict
        """

        # TODO: omit obsolete parameters, add input parameters into dataframe
        ds = {}
        ds['c_s'] = .43  # length of chord single
        ds['c_t'] = ds['c_s'] / 2  # length of chord tandem
        ds['th'] = self.rth
        ds['r_te'] = self.th_te

        # Lieblein Diffusion Factor for front and rear blade
        ds['gammahk_t1'] = .14
        ds['gammahk_t2'] = .14

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

    def thickness_dist_v1(self):
        """
        Calculate thickness distribution.
        Returns  vector with X and Y of thickness distribution.

        :return: xy_th
        :rtype xy_th: (npts, 2) ndarray
        """
        ds = self.ds
        x = self.x
        th = ds.th[0]/10
        # Option 1: Simple

        yth = th * (1 - x) * (1.0675 * np.sqrt(x) - x * (.2756 - x * (2.4478 - 2.8385 * x))) / (
                1 - .176 * x)  # thickness distribution
        # scale thickness
        th_noscale = np.zeros((self.npts, 2))
        th_noscale[:, 0] = x
        th_noscale[:, 1] = yth
        min_max_scaler = preprocessing.MinMaxScaler()
        xy_th = min_max_scaler.fit_transform(th_noscale)
        xy_th[:, 1] = xy_th[:, 1] * th

        return xy_th

    def thickness_dist_v2(self):
        # Option 2: NACA65 (Parabolic_Camber_V5)
        ds = self.ds
        x = self.x
        xd = self.x_max_th
        rn = self.th_le / self.c
        d = self.rth
        dhk = 2 * self.th_te / self.c

        c = 1
        gammahk = ds.gammahk_t1.values
        x_short = x[np.where(x < (1 - self.th_te / self.c))]

        x_front = x_short[np.where(x_short < xd)]
        y_th_front = .5 * (np.sqrt(2 * rn) * np.sqrt(x_front)
                           + (((3 * d) / xd) - (15 / 8) * np.sqrt(2 * rn / xd) - (3 * xd * (d - dhk)) / (
                        (c - xd) ** 2) + (2 * xd * np.tan(gammahk / 2)) / (c - xd)) * x_front
                           + ((5 / 4) * np.sqrt((2 * rn) / (xd ** 3)) - (3 * d) / (xd ** 2) - (
                        4 * np.tan(gammahk / 2)) / (c - xd) + (6 * (d - dhk)) / ((c - xd) ** 2)) * x_front ** 2
                           + ((2 * np.tan(gammahk / 2)) / (xd * (c - xd)) - (3 * (d - dhk)) / (
                        xd * (c - xd) ** 2) - (3 / 8) * np.sqrt((2 * rn) / (xd ** 5)) + d / (
                                      xd ** 3)) * x_front ** 3
                           )

        x_rear = x_short[np.where(x_short >= xd)]
        y_th_rear = .5 * (dhk + (2 * np.tan(gammahk / 2)) * (c - x_rear)
                          + (((3 * (d - dhk)) / (c - xd) ** 2) - (4 * np.tan(gammahk / 2)) / (c - xd)) * (
                                  c - x_rear) ** 2
                          + (((2 * np.tan(gammahk / 2)) / (c - xd) ** 2) - ((2 * (d - dhk)) / (c - xd) ** 3)) * (
                                  c - x_rear) ** 3
                          )
        yth = np.concatenate([y_th_front, y_th_rear])

        # fit trailing edge
        r_te = yth[-1]

        yth_circ_te = np.array(
            [np.sqrt(np.abs(r_te ** 2 - (X - (1 - r_te)) ** 2)) if (X > (1 - self.th_te / self.c)) else np.nan for X
             in x])
        # omit nans
        yth_circ_te = yth_circ_te[np.where(np.isnan(yth_circ_te) == False)]
        xy_th = np.zeros((x.size, 2))
        xy_th[:, 0] = x

        if (np.abs(x.size - yth.size - yth_circ_te.size) == 0):
            xy_th[:, 1] = np.concatenate([np.abs(yth), np.abs(yth_circ_te)])
        else:
            xy_th[:, 1] = np.concatenate([np.abs(yth), np.abs(yth_circ_te), [0]])

        chi_camber = np.arctan(np.gradient(self.xy_camber[:, 1]) / np.gradient(self.xy_camber[:, 0]))
        xss = x - np.sin(chi_camber) * xy_th[:, 1]
        xps = x + np.sin(chi_camber) * xy_th[:, 1]
        yss = self.xy_camber[:, 1] + np.cos(chi_camber) * xy_th[:, 1]
        yps = self.xy_camber[:, 1] - np.cos(chi_camber) * xy_th[:, 1]

        # concatenate arrays
        x_blade = np.zeros(xss.size + xps.size)
        y_blade = np.zeros(x_blade.size)
        x_blade[:xps.size] = xps[::-1]
        x_blade[xps.size:] = xss[0:]
        x_blade[xps.size] = x_blade[xps.size + 1] / 2
        y_blade[:yps.size] = yps[::-1]
        y_blade[yps.size:] = yss[0:]
        y_blade[xps.size] = y_blade[xps.size + 1] / 2

        # scale and rotate
        x_blade = x_blade * self.c
        y_blade = y_blade * self.c
        x_blade = np.cos(self.lambd) * x_blade - np.sin(self.lambd) * y_blade
        y_blade = np.sin(self.lambd) * x_blade + np.cos(self.lambd) * y_blade

        df = pd.DataFrame(data={'x': x_blade, 'y': y_blade})
        return df

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

    def geom_gen(self, xy_th, lambd, c):
        """
        Generate the Blade shape.
        Returns vector with X and Y of blade geometry.

        :param lambd: Rotation of blade
        :type lambd: float
        :param c: chord length
        :type c: float
        :param xy_th: X and Y points from method thickness_dist_v1
        :type xy_th: (npts, 2) float-array
        :param xy_camber: X and Y points from method camberline
        :type xy_camber: (npts, 2) float-array
        :return: xy_blade
        :rtype xy_blade: (npts, 2) float-array
        """
        xy_camber = self.xy_camber
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

        if (self.thdist_option == 0):
            # Trailing edge radius fitting
            if (self.th_te > 0):
                xsurface, ysurface = RoundEdges('TE', xsurface, ysurface, self.th_te / 2,
                                                xy_camber * self.c).return_xy()

            # Leading edge radius fitting
            if (self.th_le > 0):
                xsurface, ysurface = RoundEdges('LE', xsurface, ysurface, self.th_le / 2,
                                                xy_camber * self.c).return_xy()

            # scale back to original length
            # norm blade
            xlen = xsurface.max() - xsurface.min()
            xsurface = (xsurface / xlen) * c

        # rotate
        X = np.cos(lambd) * xsurface - np.sin(lambd) * ysurface
        Y = np.sin(lambd) * xsurface + np.cos(lambd) * ysurface
        xy_blade = np.transpose(np.array([X, Y]))

        # pack into pd Frame
        xy_blade = pd.DataFrame(data={'x': xy_blade[:, 0], 'y': xy_blade[:, 1]})
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

        # LE/TE Radius doesnt work properly outside of range
        assert (((rth_le <= .03) and (rth_le >= .01)) or rth_le == 0), "rth_le out of range"
        assert (((rth_te <= .03) and (rth_te >= .01)) or rth_te == 0), "rth_te out of range"

        assert ((x_maxcamber > 0) and (x_maxcamber < 1)), "x max chamber out of range [0,1]."
        # Blade arc flips above sum(beta1,beta2)>90
        assert ((beta1 + beta2) <= 90), "Beta1 + Beta2 must be smaller than 90"

        # Blade looks absolute horrible sub 500 points. Blade will be divided into 4 even parts, so npts%4==0
        # must be true.
        assert ((npts >= 500) and (npts % 4 == 0)), "Choose more than 500 Pts and npts must be dividable by 4."

    def debug_plot(self, xy_th, xy_camber, xy_blade):
        plt.figure(figsize=(12, 4))
        # plt.subplot(131)
        # plt.plot(self.x, xy_th[:, 1])
        # plt.subplot(132)
        # plt.subplot(133)
        if (np.all(self.xy_in) != None):
            plt.plot(self.xy_in.x, self.xy_in.y)
        plt.plot(xy_blade.x, xy_blade.y)
        # plt.plot(self.x, xy_camber[:, 1])
        plt.axis('equal')
        plt.legend(['imported blade', 'generated blade'])
        plt.show()

    def _return(self):
        xy_blade = self.xy_blade.values
        return xy_blade


if __name__ == "__main__":
    BladeGen(file='../geo_output/coords.txt', th_dist_option=1, lambd=28, rth_te=0.01, rth_le=.01,
             l_chord=40, beta2=25, beta1=25, r_th=.04, x_maxth=.4)
