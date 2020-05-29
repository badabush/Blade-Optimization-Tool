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


def shape_circle(side, edge, r, xy_mid, xy, idx):
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
    if (side == 'up') and (edge == 'TE'):
        nc = np.count_nonzero(
            np.isnan(xy[0])) + 1  # count nan elements of upper (+2 avoid overlap @ start- and endpoint)
        theta = np.linspace(0, np.pi / 2, nc)
    elif (side == 'low') and (edge == 'TE'):
        nc = np.count_nonzero(np.isnan(xy[0])) + 1
        theta = np.linspace(2 * np.pi, np.pi * 1.5, nc)

    if (side == 'up') and (edge == 'LE'):
        nc = np.count_nonzero(
            np.isnan(xy[0])) + 1  # count nan elements of upper (+2 avoid overlap @ start- and endpoint)
        theta = np.linspace(1.5 * np.pi, np.pi, nc)
    elif (side == 'low') and (edge == 'LE'):
        nc = np.count_nonzero(np.isnan(xy[0])) + 1
        theta = np.linspace(np.pi * 1.5, np.pi * 2, nc)

    # generate quarter-circle
    xc = (r * np.cos(theta) + xy_mid[0])
    xc = xc[::-1]
    yc = (r * np.sin(theta) + xy_mid[1])
    yc = yc[::-1]

    # calculate angle to rotate circle
    AB = [xc[0] - xy_mid[0], yc[0] - xy_mid[1]]
    AC = [xy[0][idx] - xy_mid[0], xy[1][idx] - xy_mid[1]]
    rot_angle = np.arctan2(np.linalg.norm(np.cross(AB, AC)), np.linalg.norm(np.dot(AB, AC)))

    # reinitiate circle with angular correction
    if edge == 'TE':
        if side == 'up':
            xc = r * np.cos(theta - rot_angle) + xy_mid[0]
            xc = xc[::-1] #+ np.abs(xc[-1] - xy[0][idx])  # flip array
            yc = r * np.sin(theta - rot_angle) + xy_mid[1]
            yc = yc[::-1]
            yc[1:] = yc[1:]# + np.abs(yc[0] - xy[1][idx])

            # write quarter circle into surface array, start and endpoint are left out due to overlaps
            xy[0][np.isnan(xy[0])] = xc[1:]
            xy[1][np.isnan(xy[1])] = yc[1:]
        else:
            xc = r * np.cos(theta - rot_angle) + xy_mid[0]
            xc = xc[::-1] #+ np.abs(xc[-1] - xy[0][idx])
            yc = r * np.sin(theta - rot_angle) + xy_mid[1]
            yc = yc[::-1]
            yc[1:] = yc[1:] #- np.abs(yc[0] - xy[1][idx])

            # write quarter circle into surface array, startpoint is left out due to overlaps
            xy[0][np.isnan(xy[0])] = xc[1:]
            xy[1][np.isnan(xy[1])] = yc[1:]
    else:
        if side == 'up':
            xc = r * np.cos(theta - rot_angle) + xy_mid[0]
            xc = xc[::-1]  # - np.abs(xc[-1] - xy[0][idx])  # flip array
            yc = r * np.sin(theta - rot_angle) + xy_mid[1]
            yc = yc[::-1]  # - np.abs(yc[-1] - xy[1][idx])
            yc[1:] = yc[1:] #+ np.abs(yc[0] - xy[1][idx])

            # write quarter circle into surface array, start and endpoint are left out due to overlaps
            xy[0][np.isnan(xy[0])] = xc[1:]
            xy[1][np.isnan(xy[1])] = yc[1:]
        else:
            xc = r * np.cos(theta - rot_angle) + xy_mid[0]
            xc = xc[::-1]  # + np.abs(xc[-1] - xy[0][idx])
            yc = r * np.sin(theta - rot_angle) + xy_mid[1]
            yc = yc[::-1]
            yc[1:] = yc[1:] #+ np.abs(yc[0] - xy[1][idx])

            # write quarter circle into surface array, startpoint is left out due to overlaps
            xy[0][np.isnan(xy[0])] = xc[1:]
            xy[1][np.isnan(xy[1])] = yc[1:]

    return xy[0], xy[1]


def rte_fitter(edge, x, y, r, camberline):
    """
    Fit trailing edge radius.

    Calculate euclidean distance between points, take shortest for every points, find distance closest to r_te.
    Returns X, Y coords with fitted trailing edge radius.

    :param edge: trailing or leading edge (TE/LE)
    :type edge: str
    :param x: unrotated x coords of blade
    :type x: ndarray
    :param y: unrotated y coords of blade
    :type y: ndarray
    :param r: radius of trailing edge
    :type r: float
    :return: x,y
    :rtype: ndarray
    """
    n4 = int(np.round(x.size / 4))  # forth of length

    # extract half of blade, seperated into upper and lower
    if edge == 'TE':
        xupper = x[n4 * 3:]
        yupper = y[n4 * 3:]
        xlower = x[:n4]
        xlower = xlower[::-1]
        ylower = y[:n4]
        ylower = ylower[::-1]

    else:

        xupper = x[n4 * 2:n4 * 3]
        yupper = y[n4 * 2:n4 * 3]
        xlower = x[n4:n4 * 2]
        xupper = xupper[::-1]
        ylower = y[n4:n4 * 2]
        yupper = yupper[::-1]

        xllower = x[0:n4 * 2]
        # shift points between upper and lower so points represent the opposite better
        # get offset
        offset = np.zeros(xllower.size)
        for i in range(0, xllower.size):
            offset[i] = np.abs(xupper[0] - xllower[i])
        minoffset = offset.argmin()
        real_offset = n4 - minoffset

        # shift
        xlower = x[n4 + real_offset:n4 * 2 + real_offset]
        ylower = y[n4 + real_offset:n4 * 2 + real_offset]
        xupper = x[n4 * 2 + real_offset:n4 * 3 + real_offset][::-1]
        yupper = y[n4 * 2 + real_offset:n4 * 3 + real_offset][::-1]

    dist = np.zeros((xupper.size, xupper.size))
    ds = pd.DataFrame(data={
        'xlower': xlower,
        'ylower': ylower,
        'xupper': xupper,
        'yupper': yupper,
        'idx_closest': np.zeros(xupper.size),
        'dist_closest': np.zeros(xupper.size)
    })

    # find closest upper surface point to each lower surface point
    for i in range(0, xupper.size):
        for j in range(0, xupper.size):
            dist[i][j] = euclidean_dist(xlower[i], xupper[j], ylower[i], yupper[j])

            # if (np.abs(j - i) > 2):
            #     dist[i][j] = 9999
        # find the 2 closest points with the smallest divergence to the distance 2r
        ds.idx_closest[i] = dist[i, :].argmin()
        ds.dist_closest[i] = np.abs(dist[i][int(ds.idx_closest[i])] - r * 2)

    # extract idx for lower and upper surface
    idx_low = int(ds.dist_closest.idxmin())
    idx_up = int(ds.idx_closest[idx_low])

    # cut everything behind the index
    if edge == 'TE':
        ds.xlower[ds.xlower.index.values.astype(int) > idx_low] = np.nan
        ds.ylower[ds.ylower.index.values.astype(int) > idx_low] = np.nan
        ds.xupper[ds.xupper.index.values.astype(int) > idx_up] = np.nan
        ds.yupper[ds.yupper.index.values.astype(int) > idx_up] = np.nan
    else:
        ds.xlower[ds.xlower.index.values.astype(int) > idx_low] = np.nan
        ds.ylower[ds.ylower.index.values.astype(int) > idx_low] = np.nan
        ds.xupper[ds.xupper.index.values.astype(int) > idx_up] = np.nan
        ds.yupper[ds.yupper.index.values.astype(int) > idx_up] = np.nan

    # create a half-circular-esque trailing edge
    xc_mid = ds.xlower[idx_low] + (ds.xupper[idx_up] - ds.xlower[idx_low]) / 2
    yc_mid = ds.ylower[idx_low] + (ds.yupper[idx_up] - ds.ylower[idx_low]) / 2

    # add circles to existing arrays in the df and filling up the NaNs
    ds.xupper, ds.yupper = shape_circle('up', edge, r, [xc_mid, yc_mid], [ds.xupper, ds.yupper], idx_up)
    ds.xlower, ds.ylower = shape_circle('low', edge, r, [xc_mid, yc_mid], [ds.xlower, ds.ylower], idx_low)

    # update original x and y
    if edge == 'TE':

        x[n4 * 3:] = ds.xupper
        y[n4 * 3:] = ds.yupper
        x[:n4] = ds.xlower[::-1]
        y[:n4] = ds.ylower[::-1]
    else:
        # x[n4 * 2:n4 * 3] = ds.xupper[::-1]
        # y[n4 * 2:n4 * 3] = ds.yupper[::-1]
        # x[n4:n4 * 2] = ds.xlower
        # y[n4:n4 * 2] = ds.ylower
        x[n4 * 2 + real_offset:n4 * 3 + real_offset] = ds.xupper[::-1]
        y[n4 * 2 + real_offset:n4 * 3 + real_offset] = ds.yupper[::-1]
        x[n4 + real_offset + 1:n4 * 2 + real_offset + 1] = ds.xlower  # +1 because of overlap nose
        y[n4 + real_offset + 1:n4 * 2 + real_offset + 1] = ds.ylower

    # plt.plot(ds.xupper, ds.yupper)
    # plt.plot(ds.xlower, ds.ylower)
    # plt.plot(ds.xlower[idx_low], ds.ylower[idx_low], 'x')
    # plt.plot(ds.xupper[idx_up], ds.yupper[idx_up], 'x')
    # plt.plot(xc_mid, yc_mid, 'x')
    # xcamber = camberline[200:, 0]
    # ycamber = camberline[200:, 1]
    # plt.plot(xcamber, ycamber, '--')
    # plt.plot(ds.xupper, ds.yupper, 'x')
    # plt.plot(ds.xlower, ds.ylower, 'x')

    # plt.show()

    return x, y
