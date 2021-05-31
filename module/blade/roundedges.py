import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from numpy.linalg import norm as norm
from blade.bladetools import euclidean_dist, min_dist

class RoundEdges:
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

    def return_xy(self):
        x = self.x
        y = self.y
        return x, y

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
        })

        # find closest upper surface point to each lower surface point
        dist = np.array(
            [euclidean_dist([ds.xupper, ds.yupper], [ds.xlower.iloc[i], ds.ylower.iloc[i]]) for i in
             range(0, self.n4)])
        # if points are further apart than 2 indices in LE, set distance high (reduces clipping)
        if self.edge == 'LE':
            dist = np.array(
                [dist[x, y] if np.abs(x - y) < 2 else 9999 for x in range(0, self.n4) for y in range(0, self.n4)])
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
        if self.edge == 'LE':
            self.r = self.r * 1.0
        ds.xupper, ds.yupper = self.shape_circle('up', [xc_mid, yc_mid], [ds.xupper, ds.yupper], idx_up)
        ds.xlower, ds.ylower = self.shape_circle('low', [xc_mid, yc_mid], [ds.xlower, ds.ylower], idx_low)

        ds, xy_intersect = self.attach_circle(ds)

        # smooth out the intersect point of nose/tail. Point will be projected onto the line between the 2 last points
        # from upper and lower, distance halved, new point created on half of new line between those again.
        # Different for LE and TE edge since the blade starts and ends @ TE edge. If treated similar, TE edge will not
        # be connected.
        x_circle = np.concatenate((ds.xupper[idx_up:].values, ds.xlower[idx_low:][::-1].values))
        y_circle = np.concatenate((ds.yupper[idx_up:].values, ds.ylower[idx_low:][::-1].values))
        if self.edge == 'LE':
            idx_intersect = np.where(x_circle == xy_intersect[0])
            idx_low_last = np.min(idx_intersect) - 2
            idx_up_last = np.max(idx_intersect) - 1
            xy_low_last = np.array([x_circle[idx_low_last], y_circle[idx_low_last]])
            xy_up_last = np.array([x_circle[idx_up_last], y_circle[idx_up_last]])
            xy_point = np.array([x_circle[idx_low_last + 1], y_circle[idx_low_last + 1]])
            xy_half_uplow = xy_low_last + (xy_up_last - xy_low_last) / 2
            xy_half_p = xy_half_uplow + (xy_point - xy_half_uplow) / 2

            x_circle[idx_low_last + 1] = xy_half_p[0]
            y_circle[idx_low_last + 1] = xy_half_p[1]
            x_circle[idx_up_last - 1] = xy_half_p[0]
            y_circle[idx_up_last - 1] = xy_half_p[1]
            ds.xupper.iloc[idx_up:] = x_circle[:idx_up_last + 1]
            ds.yupper.iloc[idx_up:] = y_circle[:idx_up_last + 1]
            ds.xlower.iloc[idx_low:] = x_circle[idx_low_last + 3:][::-1]
            ds.ylower.iloc[idx_low:] = y_circle[idx_low_last + 3:][::-1]

        # Fit back into original x and y
        if self.edge == 'TE':
            self.x[self.n4 * 3:] = ds.xupper
            self.y[self.n4 * 3:] = ds.yupper
            self.x[:self.n4] = ds.xlower[::-1]
            self.y[:self.n4] = ds.ylower[::-1]
        else:
            self.x[self.n4 * 2:self.n4 * 3] = ds.xupper[::-1]
            self.y[self.n4 * 2:self.n4 * 3] = ds.yupper[::-1]
            self.x[self.n4:self.n4 * 2] = ds.xlower
            self.y[self.n4:self.n4 * 2] = ds.ylower

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

            # compute max gradient of x and y to find the point where the circle is attached to the blade.
            xgrad = np.abs(np.gradient(x))
            xgrad_max = np.array([xgrad[i - 1] - xgrad[i] for i in range(1, x.size)]).argmax()
            ygrad = np.abs(np.gradient(y))
            ygrad_max = np.array([ygrad[i - 1] - ygrad[i] for i in range(1, y.size)]).argmax()

            # for some reason this fixes npts input of e.g. 700 and 1220, where the gradients of x and y has a greater
            # divergence.
            if np.abs(xgrad_max - ygrad_max) > 2:
                offset = 1
            else:
                offset = 2
            grad_idx = np.min([xgrad_max, ygrad_max]) + offset

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

        def calc_angle(edge, xy1, xy2):
            """
            Rotate circle to fit the blade by calculating the  angle, so the start of circle will be an extension
            of the blade surface.
            Returns x and y coords of fitted circle.

            :param edge: 'LE' or 'TE'
            :type edge: str
            :param xy1: list of pd.Series with x1 and y1
            :type xy1: list
            :param xy2: list of pd.Series with x2 and y2
            :type xy2: list
            :return: xn, yn
            :rtype xn: pdSeries
            :rtype yn: pdSeries
            """
            x1 = xy1[0]
            y1 = xy1[1]
            x2 = xy2[0]
            y2 = xy2[1]
            
            coef = np.polyfit([x1.iloc[-1], x1.iloc[-2]], [y1.iloc[-1], y1.iloc[-2]], 1)
            polynomial = np.poly1d(coef)
            xn_ = x2.iloc[1]
            yn_ = polynomial(xn_)

            #
            AB = [xn_ - x1.iloc[-1], yn_ - y1.iloc[-1]]
            AC = [x2.iloc[1] - x1.iloc[-1], y2.iloc[1] - y1.iloc[-1]]
            if edge == 'LE':
                if (AB[1] > AC[1]):
                    sign = -1
                else:
                    sign = 1
            else:
                if (AB[1] > AC[1]):
                    sign = 1
                else:
                    sign = -1
            angle = sign * np.arctan2(np.linalg.norm(np.cross(AB, AC)), np.linalg.norm(np.dot(AB, AC)))
            xog, yog = [x2.iloc[0], y2.iloc[0]]
            xn = xog + np.cos(angle) * (x2 - xog) - np.sin(angle) * (y2 - yog)
            yn = yog + np.sin(angle) * (x2 - xog) + np.cos(angle) * (y2 - yog)
            return xn, yn, polynomial


        # compute camber line polynomial model
        weights = np.polyfit(self.camberline[:, 0], self.camberline[:, 1], 3)
        polynomial_cl = np.poly1d(weights)

        xlower1, ylower1, xlower2, ylower2 = seperate_surface(ds.xlower, ds.ylower)
        xupper1, yupper1, xupper2, yupper2 = seperate_surface(ds.xupper, ds.yupper)

        xlower2, ylower2, polynomial_low = calc_angle(self.edge, [xlower1, ylower1], [xlower2, ylower2])
        xupper2, yupper2, polynomial_up = calc_angle(self.edge, [xupper1, yupper1], [xupper2, yupper2])

        # move lower/upper along line until it collides with upper
        # intersect with camberline

        y_up_cl = polynomial_cl(xupper2)
        idx_up, *_ = min_dist(np.array([xupper2.values, yupper2.values]), np.array([xupper2.values, y_up_cl]))
        x_up_cl = xupper2.iloc[idx_up]

        y_low_cl = polynomial_cl(xlower2)
        idx_low, *_ = min_dist(np.array([xlower2.values, ylower2.values]), np.array([xlower2.values, y_low_cl]))
        x_low_cl = xlower2.iloc[idx_low]

        xlower2 = xlower2 + (x_up_cl - x_low_cl)
        yoffset = np.abs(ylower2.iloc[0] - polynomial_low(xlower2.iloc[0]))
        ylower2 = ylower2 - yoffset

        idx_low, idx_up, *_ = min_dist(np.array([xlower2, ylower2]), np.array([xupper2, yupper2]))

        # Find indices and replace anything greater than the indices with NaNs.
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
        if self.edge == 'LE':
            ds.xlower = self.fill_interpolate(xlower1, xnlower2, x_intersect)
            ds.ylower = self.fill_interpolate(ylower1, ynlower2, y_intersect)

            ds.xupper = self.fill_interpolate(xupper1, xnupper2, x_intersect)
            ds.yupper = self.fill_interpolate(yupper1, ynupper2, y_intersect)

        return ds, [x_intersect, y_intersect]

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
        empt = np.zeros(int(diff) - 1)
        empt[:] = None
        xn = pd.Series(data=np.concatenate([p1.values, empt, p2.values, [np.nan]]))

        xn.iloc[-1] = pnose
        xn = xn.interpolate()

        return xn

    def debug_plot(self, xy_pre, xy_new, ds):
        plt.figure(figsize=(8, 12))
        plt.plot(xy_new[0], xy_new[1], 'rx')
        plt.plot(xy_new[0], xy_new[1])
        plt.plot(xy_pre[0], xy_pre[1], 'k--')
        plt.plot(self.camberline[:, 0], self.camberline[:, 1], '--')
        plt.axis('equal')
        plt.show()
