import numpy as np
from scipy.interpolate import BSpline
from matplotlib import pyplot as plt
import pandas as pd
from numpy.linalg import norm as norm


def euclidean_dist(x1, x2, y1, y2):
    """
    Returns the euclidean distance between two points.

    :param x1: x-coord of 1st point
    :type x1: float
    :param x2: x-coord of 2nd point
    :type x2: float
    :param y1: y-coord of 1st point
    :type y1: float
    :param y2: y-coord of 2nd point
    :type y2: float
    :return: euclid_dist
    :rtype: float
    """

    euclid_dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return euclid_dist


def euclidean_dist2(xy1, xy2):
    x1 = xy1[0]
    y1 = xy1[1]
    x2 = xy2[0]
    y2 = xy2[1]

    euclid_dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return euclid_dist


def min_dist(xy1, xy2):
    """
    Find closest upper surface point to each lower surface point.
    Returns idx for both arrays where the minimum distance was found as well as the distance.

    :param xy1: list arrays of x and y values
    :type xy1: list
    :param xy2: list arrays of x and y values
    :return: idx1, idx2, dist
    :rtype idx1: int
    :rtype idx2: int
    :rtype dist: float
    """

    dist = np.array(
        [euclidean_dist2(xy1[:, i], xy2[:, j]) for i in range(0, xy1.shape[1]) for j in range(0, xy2.shape[1])])
    idx1, idx2 = np.unravel_index(dist.argmin(), (xy1.shape[1], xy2.shape[1]))
    return idx1, idx2, dist.min()


class radius_fitter:
    """
    Class for fitting in leading edge and/or trailing edge radius.
    Either the front half (for LE fitting) or the latter half (for TE fitting) will be taken from input.
    A quarter circle will be attached to upper and lower surfaces, rotated into position for a smooth transition.
    The intersection between the quarter circles will be determined and cut, emerged gap will be filled with
    interpolation.

    Returns the x,y coordinates of original length with the fitted radius.

    :param edge: TE/LE
    :type edge: str
    :param x: x coordinates of whole blade
    :type x: ndarray
    :param y: y coordinates of whole blade
    :type y: ndarray
    :param r: radius of LE/TE circle
    :type r: float
    :param camberline: xy of camberline
    :type camberline: list of ndarrays

    :return: x, y
    :rtype x: ndarray
    :rtype y: ndarray
    """

    def __init__(self, edge, x, y, r, camberline):
        self.edge = edge
        self.x = x
        self.y = y
        self.r = r
        self.camberline = camberline
        self.n4 = int(np.round(x.size / 4))  # quarter length of original input coords
        ds, idx_low, idx_up = self.prior_geom()
        self.fit_circle(ds, idx_low, idx_up)

        self.return_xy()

    def return_xy(self):
        x = self.x
        y = self.y
        return [x, y]

    def prior_geom(self):
        """
        Extract front or latter half of blade, seperated to upper and lower.
        Find distance between upper and lower surface points matching input radius, cutting geometry after the point.
        Create and returns dataset containing xylower, xyupper, ....

        :return: ds
        :rtype ds: pdDataFrame
        """
        # extract half of blade, seperated into upper and lower
        if self.edge == 'TE':
            xupper = self.x[self.n4 * 3:]
            yupper = self.y[self.n4 * 3:]
            xlower = self.x[:self.n4]
            xlower = xlower[::-1]
            ylower = self.y[:self.n4]
            ylower = ylower[::-1]

        else:

            xupper = self.x[self.n4 * 2:self.n4 * 3]
            yupper = self.y[self.n4 * 2:self.n4 * 3]
            xlower = self.x[self.n4:self.n4 * 2]
            xupper = xupper[::-1]
            ylower = self.y[self.n4:self.n4 * 2]
            yupper = yupper[::-1]

        ds = pd.DataFrame(data={
            'xlower': xlower,
            'ylower': ylower,
            'xupper': xupper,
            'yupper': yupper
            # 'idx_closest': np.zeros(xupper.size),
            # 'dist_closest': np.zeros(xupper.size)
        })
        # find closest upper surface point to each lower surface point

        dist = np.array(
            [euclidean_dist2([ds.xupper, ds.yupper], [ds.xlower.iloc[i], ds.ylower.iloc[i]]) for i in range(0, 250)])
        # if points are further apart than 2 indices in LE, set distance high (reduces clipping)
        if self.edge == 'LE':
            dist = np.array([dist[x, y] if np.abs(x - y) < 2 else 9999 for x in range(0, 250) for y in range(0, 250)])
            dist = dist.reshape(self.n4, self.n4)
        idx_closest = dist.argmin(axis=1)
        dist_closest = np.array([np.abs(dist[i, idx_closest[i].astype(int)] - self.r * 2) for i in range(0, self.n4)])
        # extract idx for lower and upper surface
        idx_low = int(dist_closest.argmin())
        idx_up = int(idx_closest[idx_low])

        # cut everything behind the index
        if self.edge == 'TE':
            ds.xlower[ds.xlower.index.values.astype(int) > idx_low] = np.nan
            ds.ylower[ds.ylower.index.values.astype(int) > idx_low] = np.nan
            ds.xupper[ds.xupper.index.values.astype(int) > idx_up] = np.nan
            ds.yupper[ds.yupper.index.values.astype(int) > idx_up] = np.nan
        else:
            ds.xlower[ds.xlower.index.values.astype(int) > idx_low] = np.nan
            ds.ylower[ds.ylower.index.values.astype(int) > idx_low] = np.nan
            ds.xupper[ds.xupper.index.values.astype(int) > idx_up] = np.nan
            ds.yupper[ds.yupper.index.values.astype(int) > idx_up] = np.nan

        return ds, idx_low, idx_up

    def fit_circle(self, ds, idx_low, idx_up):

        # create a half-circular-esque trailing edge
        xc_mid = ds.xlower[idx_low] + (ds.xupper[idx_up] - ds.xlower[idx_low]) / 2
        yc_mid = ds.ylower[idx_low] + (ds.yupper[idx_up] - ds.ylower[idx_low]) / 2

        # add circles to existing arrays in the df and filling up the NaNs
        self.r = self.r * 1.05
        ds.xupper, ds.yupper = self.shape_circle('up', [xc_mid, yc_mid], [ds.xupper, ds.yupper], idx_up)
        ds.xlower, ds.ylower = self.shape_circle('low', [xc_mid, yc_mid], [ds.xlower, ds.ylower], idx_low)

        ds = self.attach_circle(ds)
        if self.edge == 'TE':
            # fix clipping
            self.x[self.n4 * 3:] = ds.xupper
            self.y[self.n4 * 3:] = ds.yupper
            self.x[:self.n4] = ds.xlower[::-1]
            self.y[:self.n4] = ds.ylower[::-1]
        else:
            # fix clipping
            self.x[self.n4 * 2:self.n4 * 3] = ds.xupper[::-1]
            self.y[self.n4 * 2:self.n4 * 3] = ds.yupper[::-1]
            self.x[self.n4:self.n4 * 2] = ds.xlower
            self.y[self.n4:self.n4 * 2] = ds.ylower

        0

    def shape_circle(self, side, xy_mid, xy, idx):
        """
        Takes either the upper or lower surface and adds a quarter circle where the original shape was.

        :param side: either 'up' or 'low' to differentiate between both sides since overlaps will be handled differently
        :type side: str
        :param edge: either 'LE' or 'TE'
        :type edge: str
        :param r: radius
        :type r: float
        :param xy_mid: X,Y coord. for the origin of circle
        :type xy_mid: (n, 2) ndarray
        :param xy: X,Y coord. for the upper or lower surface
        :type xy: (n, 2) ndarray
        :param idx: index of last point that is not NaN of upper or lower surface
        :type idx: int
        :return: xy
        :rtype xy: (n, 2) ndarray
        """

        # since length is different for upper and lower array, the "erased" length will be recreated to be a  quarter circle
        # from endpoint to mid
        if (side == 'up') and (self.edge == 'TE'):
            nc = np.count_nonzero(
                np.isnan(xy[0])) + 1  # count nan elements of upper (+2 avoid overlap @ start- and endpoint)
            theta = np.linspace(0, np.pi / 2, nc)
        elif (side == 'low') and (self.edge == 'TE'):
            nc = np.count_nonzero(np.isnan(xy[0])) + 1
            theta = np.linspace(2 * np.pi, np.pi * 1.5, nc)

        if (side == 'up') and (self.edge == 'LE'):
            nc = np.count_nonzero(
                np.isnan(xy[0])) + 1  # count nan elements of upper (+2 avoid overlap @ start- and endpoint)
            theta = np.linspace(1.5 * np.pi, np.pi, nc)
        elif (side == 'low') and (self.edge == 'LE'):
            nc = np.count_nonzero(np.isnan(xy[0])) + 1
            theta = np.linspace(np.pi * 1.5, np.pi * 2, nc)

        # generate quarter-circle
        xc = (self.r * np.cos(theta) + xy_mid[0])
        xc = xc[::-1]
        yc = (self.r * np.sin(theta) + xy_mid[1])
        yc = yc[::-1]

        # calculate angle to rotate circle
        AB = [xc[0] - xy_mid[0], yc[0] - xy_mid[1]]
        AC = [xy[0][idx] - xy_mid[0], xy[1][idx] - xy_mid[1]]
        rot_angle = np.arctan2(np.linalg.norm(np.cross(AB, AC)), np.linalg.norm(np.dot(AB, AC)))

        # reinitiate circle with angular correction
        if self.edge == 'TE':
            if side == 'up':
                xc = self.r * np.cos(theta - rot_angle) + xy_mid[0]
                xc = xc[::-1]  # + np.abs(xc[-1] - xy[0][idx])  # flip array
                yc = self.r * np.sin(theta - rot_angle) + xy_mid[1]
                yc = yc[::-1]
                yc[1:] = yc[1:]  # + np.abs(yc[0] - xy[1][idx])

                # write quarter circle into surface array, start and endpoint are left out due to overlaps
                xy[0][np.isnan(xy[0])] = xc[1:]
                xy[1][np.isnan(xy[1])] = yc[1:]
            else:
                xc = self.r * np.cos(theta - rot_angle) + xy_mid[0]
                xc = xc[::-1]  # + np.abs(xc[-1] - xy[0][idx])
                yc = self.r * np.sin(theta - rot_angle) + xy_mid[1]
                yc = yc[::-1]
                yc[1:] = yc[1:]  # - np.abs(yc[0] - xy[1][idx])

                # write quarter circle into surface array, startpoint is left out due to overlaps
                xy[0][np.isnan(xy[0])] = xc[1:]
                xy[1][np.isnan(xy[1])] = yc[1:]
        else:
            if side == 'up':
                xc = self.r * np.cos(theta - rot_angle) + xy_mid[0]
                xc = xc[::-1]  # - np.abs(xc[-1] - xy[0][idx])  # flip array
                yc = self.r * np.sin(theta - rot_angle) + xy_mid[1]
                yc = yc[::-1]  # - np.abs(yc[-1] - xy[1][idx])
                yc[1:] = yc[1:]  # + np.abs(yc[0] - xy[1][idx])

                # write quarter circle into surface array, start and endpoint are left out due to overlaps
                xy[0][np.isnan(xy[0])] = xc[1:]
                xy[1][np.isnan(xy[1])] = yc[1:]
            else:
                xc = self.r * np.cos(theta - rot_angle) + xy_mid[0]
                xc = xc[::-1]  # + np.abs(xc[-1] - xy[0][idx])
                yc = self.r * np.sin(theta - rot_angle) + xy_mid[1]
                yc = yc[::-1]
                yc[1:] = yc[1:]  # + np.abs(yc[0] - xy[1][idx])

                # write quarter circle into surface array, startpoint is left out due to overlaps
                xy[0][np.isnan(xy[0])] = xc[1:]
                xy[1][np.isnan(xy[1])] = yc[1:]

        return xy[0], xy[1]

    def attach_circle(self, ds):
        """
        Bring the circles into correct position, fix clipping in intersections (surface-circle, circle-circle),
        cut overlaps and interpolate for smooth surface.

        Returns updated ds

        :param ds: dataset of coordinates
        :type ds: pdDataFrame
        :return: ds
        :rtype ds: pdDataFrame
        """

        # compute camber line polynomial model
        weights = np.polyfit(self.camberline[:, 0], self.camberline[:, 1], 3)
        polynomial_cl = np.poly1d(weights)

        def seperate_surface(x, y):
            """
            Seperates the input surface into two parts by finding the max gradient.
            Returns 4 pdSeries x1,y1 and x2,y2, both with a combined length of n4.

            :param x: x coords of lower or upper surface
            :type x: pdSeries[n4]
            :param y: y coords of lower or upper surface
            :type y: pdSeries[n4]
            :return: x1, x2, y1, y2
            :rtype x1: pdSeries
            :rtype y1: pdSeries
            :rtype x2: pdSeries
            :rtype y2: pdSeries
            """
            xgrad = np.abs(np.gradient(x))
            xgrad_max = np.array([xgrad[i - 1] - xgrad[i] for i in range(1, x.size)]).argmax()
            ygrad = np.abs(np.gradient(y))
            ygrad_max = np.array([ygrad[i - 1] - ygrad[i] for i in range(1, y.size)]).argmax()
            grad_idx = np.min([xgrad_max, ygrad_max]) + 2

            # seperate line at max grad
            x1 = x[:grad_idx]
            x2 = x[grad_idx:]
            y1 = y[:grad_idx]
            y2 = y[grad_idx:]

            xdist = x2.iloc[0] - x1.iloc[-1]
            ydist = y2.iloc[0] - y1.iloc[-1]

            # move xy2
            x2 = x2 - xdist
            y2 = y2 - ydist

            return x1, y1, x2, y2

        xlower1, ylower1, xlower2, ylower2 = seperate_surface(ds.xlower, ds.ylower)
        xupper1, yupper1, xupper2, yupper2 = seperate_surface(ds.xupper, ds.yupper)

        # poly lower
        coef = np.polyfit([xlower1.iloc[-1], xlower1.iloc[-2]], [ylower1.iloc[-1], ylower1.iloc[-2]], 1)
        polynomial_low = np.poly1d(coef)
        xn_low = xlower2.iloc[1]
        yn_low = polynomial_low(xn_low)

        # calculate angle to rotate circle
        AB = [xn_low - xlower1.iloc[-1], yn_low - ylower1.iloc[-1]]
        AC = [xlower2.iloc[1] - xlower1.iloc[-1], ylower2.iloc[1] - ylower1.iloc[-1]]
        if self.edge == 'LE':
            if (AB[1] > AC[1]):
                sign = -1
            else:
                sign = 1
        else:
            if (AB[1] > AC[1]):
                sign = 1
            else:
                sign = -1
        angle_low = np.sign(sign) * np.arctan2(np.linalg.norm(np.cross(AB, AC)), np.linalg.norm(np.dot(AB, AC)))
        xlow_og, ylow_og = [xlower2.iloc[0], ylower2.iloc[0]]
        xlower2 = xlow_og + np.cos(angle_low) * (xlower2 - xlow_og) - np.sin(angle_low) * (ylower2 - ylow_og)
        ylower2 = ylow_og + np.sin(angle_low) * (xlower2 - xlow_og) + np.cos(angle_low) * (ylower2 - ylow_og)

        # fixme: fix repetition of script
        # poly upper
        coef = np.polyfit([xupper1.iloc[-1], xupper1.iloc[-2]], [yupper1.iloc[-1], yupper1.iloc[-2]], 1)
        polynomial_up = np.poly1d(coef)
        xn_up = xupper2.iloc[1]
        yn_up = polynomial_up(xn_up)

        # calculate angle to rotate circle
        AB = [xn_up - xupper1.iloc[-1], yn_up - yupper1.iloc[-1]]
        AC = [xupper2.iloc[1] - xupper1.iloc[-1], yupper2.iloc[1] - yupper1.iloc[-1]]
        if self.edge == 'LE':
            if (AB[1] > AC[1]):
                sign = -1
            else:
                sign = 1
        else:
            if (AB[1] > AC[1]):
                sign = -1
            else:
                sign = 1
        angle_up = np.sign(sign) * np.arctan2(np.linalg.norm(np.cross(AB, AC)), np.linalg.norm(np.dot(AB, AC)))
        xup_og, yup_og = [xupper2.iloc[0], yupper2.iloc[0]]
        xupper2 = xup_og + np.cos(angle_up) * (xupper2 - xup_og) - np.sin(angle_up) * (yupper2 - yup_og)
        yupper2 = yup_og + np.sin(angle_up) * (xupper2 - xup_og) + np.cos(angle_up) * (yupper2 - yup_og)

        # # move lower/upper along line until it collides with upper
        # intersect with camberline
        y_up_cl = polynomial_cl(xupper2)
        idx_up, foo1, foo2 = min_dist(np.array([xupper2.values, yupper2.values]), np.array([xupper2.values, y_up_cl]))
        x_up_cl = xupper2.iloc[idx_up]

        y_low_cl = polynomial_cl(xlower2)
        idx_low, foo1, foo2 = min_dist(np.array([xlower2.values, ylower2.values]), np.array([xlower2.values, y_low_cl]))
        x_low_cl = xlower2.iloc[idx_low]

        # Find indices and replace anything greater than the indices with NaNs.
        xlower2 = xlower2 + (x_up_cl - x_low_cl)
        yoffset = np.abs(ylower2.iloc[0] - polynomial_low(xlower2.iloc[0]))
        ylower2 = ylower2 - yoffset
        idx_low, idx_up, foo = min_dist(np.array([xlower2.values, ylower2.values]),
                                        np.array([xupper2.values, yupper2.values]))
        xlower2.reset_index(drop=True, inplace=True)
        ylower2.reset_index(drop=True, inplace=True)
        xupper2.reset_index(drop=True, inplace=True)
        yupper2.reset_index(drop=True, inplace=True)
        xlower2[xlower2.index >= idx_low] = np.nan
        ylower2[ylower2.index >= idx_low] = np.nan
        xupper2[xupper2.index >= idx_up] = np.nan
        yupper2[yupper2.index >= idx_up] = np.nan
        xupper2.iloc[idx_up] = xlower2.iloc[idx_low - 1]
        yupper2.iloc[idx_up] = ylower2.iloc[idx_low - 1]
        xlower2.dropna(inplace=True)
        ylower2.dropna(inplace=True)
        xupper2.dropna(inplace=True)
        yupper2.dropna(inplace=True)
        idx_low, idx_up, *_ = min_dist(np.array([xlower2, ylower2]), np.array([xupper2, yupper2]))

        # cut circles @ index and place in x,y new
        xnlower2 = xlower2.iloc[:idx_low]
        ynlower2 = ylower2.iloc[:idx_low]
        xnupper2 = xupper2.iloc[:idx_up]
        ynupper2 = yupper2.iloc[:idx_up]

        # get point of intersection
        x_intersect = xlower2.iloc[idx_low]
        y_intersect = ylower2.iloc[idx_low]

        # fit back into pandas series by interpolating NaNs
        ds.xlower = self.fill_interpolate(xlower1, xnlower2, x_intersect)
        ds.ylower = self.fill_interpolate(ylower1, ynlower2, y_intersect)

        ds.xupper = self.fill_interpolate(xupper1, xnupper2, x_intersect)
        ds.yupper = self.fill_interpolate(yupper1, ynupper2, y_intersect)

        return ds

    def fill_interpolate(self, p1, p2, pnose):
        """
        Interpolate nan values and fill into correct length (n4).
        Returns blade with new circle attached.

        :param p1: x or y blade
        :type p1: pdSeries
        :param p2: x or y circle
        :type p2: pdSeries
        :param pnose: x or y of nose point
        :type pnose:
        :return: xn
        :rtype xn: pdSeries
        """

        diff = self.n4 - p1.size - p2.size
        # even length of diff
        if (diff % 2) == 0:
            empt = np.zeros(int(diff / 2))
            empt[:] = None
            xn = pd.Series(data=np.concatenate([p1.values, empt, p2.values, empt]))
        else:
            empt1 = np.zeros(int(np.floor(diff / 2)))
            empt1[:] = None
            empt2 = np.zeros(int(np.floor(diff / 2) + 1))
            empt2[:] = None
            xn = pd.Series(data=np.concatenate([p1.values, empt1, p2.values, empt2]))

        xn.iloc[-1] = pnose
        xn = xn.interpolate()

        return xn
