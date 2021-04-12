import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt
from sklearn import preprocessing
import pandas as pd
import scipy.optimize as optimize

from blade.bladetools import ImportExport, normalize, cdist_from_spline
from blade.testspline import compute_spline
from blade.roundedges import RoundEdges


class BladeGen:
    """
    Generate a blade from parameters.
    """

    def __init__(self, frontend='user', file='', blade_df={}):
        self.file = file
        if self.file != '':
            try:
                self.xy_in = ImportExport()._import(file)
                self.xy_in = normalize(self.xy_in)
            except (ImportError, AttributeError) as e:
                print(e)

        # assert input
        self.assert_input(blade_df)
        # menu items
        self.thdist_option = blade_df["th_dist_ver"]  # th_dist v1 or v2
        self.frontend = frontend  # the interface to this script
        self.nblade = blade_df["nblades"]

        # pack parameters into dict
        self.ds = self.params(blade_df)
        self.x = .5 * (1 - np.cos(np.linspace(0, np.pi, int(self.ds['npts'] / 2))))  # x-coord generation
        # self.x = np.linspace(0, 1, self.ds['npts'])

        # #TODO: camber spline is disabled for now
        self.xy_camber = self.camberline(self.ds['theta'], self.ds["xmax_camber"])
        thdist_points = blade_df["thdist_pts"]
        # if 9999 in spline_pts:
        #     self.xy_camber = self.camberline(self.ds['theta'], x_maxcamber)
        # else:
        #     self.xy_cspline = compute_spline(spline_pts[:, 0], spline_pts[:, 1])
        #     self.xy_camber = cdist_from_spline(self.xy_cspline, self.ds['theta'])
        #     update x because spline function in spline differs x slightly (otherwise thickness dist doesnt fit spline)
        # self.x = self.xy_camber[:, 0]

        if self.thdist_option == 0:
            xy_th = self.thickness_dist_v1()
            xy_blade, self.xy_camber = self.geom_gen(xy_th)

        elif self.thdist_option == 1:
            if 9999 in thdist_points:
                xy_blade, self.xy_camber = self.thickness_dist_v2()
            else:
                xy_blade, self.xy_camber = self.thickness_dist_v2(thdist_points)

        if self.frontend == 'user':
            path = Path.cwd() / "geo_output/py"
            ImportExport()._export(path, xy_blade)
            self.debug_plot(self.xy_camber, xy_blade)

        elif self.frontend == 'UI':
            self.xy_blade = xy_blade
            self._return()

    def params(self, blade_df):
        """
        Generate parameters.
        Return dataset (ds) with parameters.

        :return: ds
        :rtype ds: dict
        """

        # TODO: omit obsolete parameters, add input parameters into dataframe
        ds = {}
        if self.nblade == 'single':
            ds['l_chord'] = blade_df["l_chord"]
            ds['chord_dist'] = 1
            ds['rth'] = blade_df["th"]  # * ds['l_chord']
            # ds['xmax_camber'] = .5  # FIXME: fixed value for spline camber development
            ds['xmax_camber'] = blade_df["xmax_camber"]
            ds['xmax_th'] = blade_df["xmax_th"]
            ds['th_le'] = blade_df["th_le"]  # * ds['l_chord']
            ds['th_te'] = blade_df["th_te"]  # * ds['l_chord']
            ds['gamma_te'] = blade_df["gamma_te"]  # Lieblein Diffusion Factor for front and rear blade
            ds['alpha'] = blade_df["alpha1"] + blade_df["alpha2"]
            ds['theta'] = np.deg2rad(np.sum(ds['alpha']))
            ds['lambd'] = np.deg2rad(blade_df["lambd"])


        elif self.nblade == 'tandem':
            # ds['l_chord'] = blade_df["l_chord"]/2
            # ds['chord_dist'] = blade_df["chord_dist"]
            # if blade_df['blade'] == "front":
            ds['l_chord'] = blade_df['chord_dist']
            # else:
            #     ds['l_chord'] = 1-blade_df['chord_dist']
            ds['rth'] = blade_df["th"]  # / ds['l_chord']
            ds['alpha'] = blade_df["alpha1"] + blade_df["alpha2"]
            ds['theta'] = np.deg2rad(np.sum(ds['alpha']))
            ds['lambd'] = np.deg2rad(blade_df["lambd"])
            ds['xmax_camber'] = blade_df["xmax_camber"]
            ds['xmax_th'] = blade_df["xmax_th"]
            ds['th_le'] = blade_df["th_le"]  # * ds['l_chord']
            ds['th_te'] = blade_df["th_te"]  # * ds['l_chord']
            ds['gamma_te'] = blade_df["gamma_te"]  # Lieblein Diffusion Factor for front and rear blade
        ds['npts'] = int(blade_df["npts"] / 2)

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
        npts = ds['npts']
        th = ds['rth']

        yth = th * (1 - x) * (1.0675 * np.sqrt(x) - x * (.2756 - x * (2.4478 - 2.8385 * x))) / (
                1 - .176 * x)  # thickness distribution
        # scale thickness
        th_noscale = np.zeros((npts, 2))
        th_noscale[:, 0] = x
        th_noscale[:, 1] = yth
        min_max_scaler = preprocessing.MinMaxScaler()
        xy_th = min_max_scaler.fit_transform(th_noscale)
        xy_th[:, 1] = xy_th[:, 1] * th

        return xy_th

    def thickness_dist_v2(self, xyth_spline=[9999, 9999]):
        # Option 2: NACA65 (Parabolic_Camber_V5)
        ds = self.ds
        xy_camber = self.xy_camber
        th_te = ds['th_te']
        th_le = ds['th_le']
        lambd = ds['lambd']
        x = self.x
        xd = ds['xmax_th']
        rn = 4 * th_le
        if self.nblade == "tandem":
            d = ds['rth'] / ds["l_chord"]  # absolute thickness ... ???
        else:
            d = ds['rth'] * 2
        # d = ds['rth']  * 2
        dhk = 2 * th_te
        c = 1
        # c = ds["l_chord"]
        gammahk = ds['gamma_te']
        # if thickness dist spline points are given, take thdist from spline
        if 0:
            if not 9999 in xyth_spline:
                xy_th = compute_spline(xyth_spline[:, 0], xyth_spline[:, 1] * ds['rth'])
                n_half = int(xy_th.shape[0] / 2)
                xy_th_front = np.array(
                    [xy_th[i, :] if xy_th[i, 1] > th_le else [xy_th[i, 0], np.nan] for i in range(0, n_half)])
                xy_th_rear = np.array([xy_th[i, :] if xy_th[i, 1] >= th_te else [xy_th[i, 0], np.nan] for i in
                                       range(n_half, xy_th.shape[0])])
                try:
                    # find position of nan entry before/after value
                    idx_front = np.argwhere(np.isnan(xy_th_front[:, 1]))[-1]
                    idx_rear = np.argwhere(np.isnan(xy_th_rear[:, 1]))[0]

                    xy_th = np.vstack((xy_th_front, xy_th_rear))
                    count_nans = np.isnan(xy_th[:, 1]).sum()
                    if count_nans > 60:
                        idx_start = int(np.floor(count_nans / 6))
                        # idx_start = int(np.floor(th_le*2000))
                        idx_end = xy_th.shape[0] - int(np.floor(count_nans / 6))
                        # idx_end = 470
                        yth = np.zeros(xy_th.shape[0])
                        pointer = int(idx_front)
                        for i in range(idx_start, idx_end):
                            if pointer > (n_half + idx_rear):
                                break
                            if i % 3 == 0:
                                # yth[i] = np.nan
                                yth[i] = xy_th[pointer, 1]
                                pointer += 2
                            else:
                                # yth[i] = xy_th[pointer,1]
                                # pointer+=1
                                yth[i] = np.nan
                    yth = pd.DataFrame({'x': xy_th[:, 0], 'y': yth})
                    yth.y.interpolate(method='piecewise_polynomial', order=5, inplace=True)
                    yth.y.loc[:n_half] = np.where((yth.y.loc[:n_half] <= th_le), np.nan, yth.y.loc[:n_half])
                    yth.y.loc[n_half:] = np.where((yth.y.loc[n_half:] <= th_te), np.nan, yth.y.loc[n_half:])
                    yth.y.iloc[0] = 0
                    yth.y.iloc[-1] = 0
                    yth.y.interpolate(method='linear', inplace=True)
                    xy_th = yth.to_numpy()
                except IndexError:
                    print("Error while rounding edges")
        # else:
        # generate y thickness dist if not given by spline
        x_short = x[np.where(x < (1 - th_te / c))]

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

        # fit trailing edge radius
        r_te = yth[-1]

        yth_circ_te = np.array(
            [np.sqrt(np.abs(r_te ** 2 - (X - (1 - r_te)) ** 2)) if (X > (1 - th_te / c)) else np.nan for X
             in x])
        # omit nans
        yth_circ_te = yth_circ_te[np.where(np.isnan(yth_circ_te) == False)]
        xy_th = np.zeros((x.size, 2))
        xy_th[:, 0] = x

        if (np.abs(x.size - yth.size - yth_circ_te.size) == 0):
            xy_th[:, 1] = np.concatenate([np.abs(yth), np.abs(yth_circ_te)])
        else:
            xy_th[:, 1] = np.concatenate([np.abs(yth), np.abs(yth_circ_te), [0]])

        self.xy_th = xy_th
        chi_camber = np.arctan(np.gradient(xy_camber[:, 1]) / np.gradient(xy_camber[:, 0]))
        xss = x - np.sin(chi_camber) * xy_th[:, 1]
        xps = x + np.sin(chi_camber) * xy_th[:, 1]
        yss = xy_camber[:, 1] + np.cos(chi_camber) * xy_th[:, 1]
        yps = xy_camber[:, 1] - np.cos(chi_camber) * xy_th[:, 1]

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
        # blade
        x_blade = x_blade * ds['l_chord']
        y_blade = y_blade * ds['l_chord']
        X = np.cos(lambd) * x_blade - np.sin(lambd) * y_blade
        Y = np.sin(lambd) * x_blade + np.cos(lambd) * y_blade
        # camber
        xy_camber = xy_camber * ds['l_chord']
        X_camber = np.cos(lambd) * xy_camber[:, 0] - np.sin(lambd) * xy_camber[:, 1]
        Y_camber = np.sin(lambd) * xy_camber[:, 0] + np.cos(lambd) * xy_camber[:, 1]

        df = pd.DataFrame(data={'x': X, 'y': Y})
        return df, np.transpose(np.array([X_camber, Y_camber]))

    def camberline(self, theta, a):
        """
        Calculate the parabolic-arc camberline from R.Aungier.
        Returns vector with X and Y of camber line.

        :param theta: sum of alpha1 and alpha2 (Chi1 and Chi2 in R.Aungier)
        :type theta: float
        :param a: max. camber position
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
            y0 = 0.0
            fun = lambda y: (-y + xtemp * (c - xtemp) / (
                    (((c - 2 * a) ** 2) / (4 * b ** 2)) * y + ((c - 2 * a) / b) * xtemp - (
                    (c ** 2 - 4 * a * c) / (4 * b))))
            y = optimize.fsolve(fun, y0)
            ycambertemp[i] = y

        xy_camber = np.transpose(np.array([x, ycambertemp]))

        return xy_camber

    def geom_gen(self, xy_th):
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
        ds = self.ds
        xy_camber = self.xy_camber
        x = self.x
        lambd = ds['lambd']
        c = ds['l_chord'] * ds['chord_dist']
        th_le = ds['th_le']
        th_te = ds['th_te']

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
        # scale with c
        xy_camber = xy_camber * c

        try:
            if (self.thdist_option == 0):
                # Trailing edge radius fitting
                if (th_te > 0):
                    xsurface, ysurface = RoundEdges('TE', xsurface, ysurface, th_te / 2,
                                                    xy_camber * c).return_xy()

                # Leading edge radius fitting
                if (th_le > 0):
                    xsurface, ysurface = RoundEdges('LE', xsurface, ysurface, th_le / 2,
                                                    xy_camber * c).return_xy()

                # scale back to original length
                # norm blade
                xlen = xsurface.max() - xsurface.min()
                xsurface = (xsurface / xlen) * c
        except ValueError as e:
            print(e)
        # rotate blade
        X = np.cos(lambd) * xsurface - np.sin(lambd) * ysurface
        Y = np.sin(lambd) * xsurface + np.cos(lambd) * ysurface
        xy_blade = np.transpose(np.array([X, Y]))
        # rotate camber line
        X_camber = np.cos(lambd) * xy_camber[:, 0] - np.sin(lambd) * xy_camber[:, 1]
        Y_camber = np.sin(lambd) * xy_camber[:, 0] + np.cos(lambd) * xy_camber[:, 1]
        xy_camber = np.transpose(np.array([X_camber, Y_camber]))

        # pack into pd Frame
        xy_blade = pd.DataFrame(data={'x': xy_blade[:, 0], 'y': xy_blade[:, 1]})
        return xy_blade, xy_camber

    def assert_input(self, df):
        """
        Assert input parameter are within defined range.

        :param nblade: number of blades, default: 'single'
        :type nblade: str
        :param r_th: relative thickness, default: .0215
        :type r_th: float
        :param alpha1: inlet angle, default: 25
        :type alpha1: float
        :param alpha2: outlet angle, default: 25
        :type alpha2: float
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
        assert ((df["nblades"] == 'single') or (df["nblades"] == 'tandem')), "single or tandem"

        # LE/TE Radius doesnt work properly outside of range
        assert (((df["th_le"] <= .03) and (df["th_le"] >= .005)) or df["th_le"] == 0), "rth_le out of range"
        assert (((df["th_te"] <= .03) and (df["th_te"] >= .005)) or df["th_te"] == 0), "rth_te out of range"

        assert ((df["xmax_camber"] > 0) and (df["xmax_camber"] < 1)), "x max chamber out of range [0,1]."
        # Blade arc flips above sum(alpha1,alpha2)>90
        assert ((df["alpha1"] + df["alpha2"]) <= 90), "alpha1 + alpha2 must be smaller than 90"

        # Blade looks absolute horrible sub 500 points. Blade will be divided into 4 even parts, so npts%4==0
        # must be true.
        assert ((df["npts"] >= 500) and (
                df["npts"] % 4 == 0)), "Choose more than 500 Pts and npts must be dividable by 4."

    def debug_plot(self, xy_camber, xy_blade):
        plt.figure(figsize=(12, 4))
        plt.plot(xy_blade.x, xy_blade.y)
        plt.plot(self.x, xy_camber[:, 1])
        plt.axis('equal')
        plt.legend(['imported blade', 'generated blade'])
        plt.grid()
        plt.show()

    def _return(self):
        xy_blade = self.xy_blade.values
        xy_camber = self.xy_camber
        return xy_blade, xy_camber


if __name__ == "__main__":
    # BladeGen(file='../geo_output/coords.txt', th_dist_option=0, lambd=0, th_te=0.00, th_le=.0,
    #          l_chord=1, alpha2=15, alpha1=15, th=.04, x_maxth=.5, spline_pts=[9999, 9999])
    from bladetools import initialize_blade_df

    df = initialize_blade_df()
    BladeGen(blade_df=df)
