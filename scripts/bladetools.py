import numpy as np
import scipy.optimize as optimize
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


def shape_circle(side, r, xy_mid, xy, idx):
    """
    Takes either the upper or lower surface and adds a quarter circle where the original shape was.

    :param side: either 'up' or 'low' to differentiate between both sides since overlaps will be handled differently
    :type side: str
    :param r: radius
    :type r: float
    :param xy_mid: X,Y coord. for the origin of circle
    :type xy_mid: (n, 2) float-array
    :param xy: X,Y coord. for the upper or lower surface
    :type xy: (n, 2) float-array
    :param idx: index of last point that is not NaN of upper or lower surface
    :type idx: int
    :return: xy
    :rtype xy: (n, 2) float-array
    """

    # since length is different for upper and lower array, the "erased" length will be recreated to be a  quarter circle
    # from endpoint to mid
    if side == 'up':
        nc = np.count_nonzero(
            np.isnan(xy[0])) + 2  # count nan elements of upper (+2 avoid overlap @ start- and endpoint)
        theta = np.linspace(0, np.pi / 2, nc)
    else:
        nc = np.count_nonzero(np.isnan(xy[0])) + 1
        theta = np.linspace(2 * np.pi, np.pi * 1.5, nc)

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
    if side == 'up':
        xc = r * np.cos(theta - rot_angle) + xy_mid[0]
        xc = xc[::-1]
        yc = r * np.sin(theta - rot_angle) + xy_mid[1]
        yc = yc[::-1] - np.abs(yc[-1] - xy[1][idx])

        # write quarter circle into surface array, start and endpoint are left out due to overlaps
        xy[0][np.isnan(xy[0])] = xc[1:-1]
        xy[1][np.isnan(xy[1])] = yc[1:-1]
    else:
        xc = r * np.cos(theta - rot_angle) + xy_mid[0]
        xc = xc[::-1] + np.abs(xc[-1] - xy[0][idx])
        yc = r * np.sin(theta - rot_angle) + xy_mid[1]
        yc = yc[::-1] + np.abs(yc[-1] - xy[1][idx])
        # write quarter circle into surface array, startpoint is left out due to overlaps
        xy[0][np.isnan(xy[0])] = xc[1:]
        xy[1][np.isnan(xy[1])] = yc[1:]

    return xy[0], xy[1]


def rte_fitter(x, y, r, camberline):
    """
    Fit trailing edge radius.

    Calculate euclidean distance between points, take shortest for every points, find distance closest to r_te.
    Returns X, Y coords with fitted trailing edge radius.

    :param x: unrotated x coords of blade
    :param y: unrotated y coords of blade
    :param r: radius of trailing edge
    :return: x,y
    :rtype: float array
    """
    n4 = int(np.round(x.size / 4))  # forth of length

    # extract the latter half of blade, seperated into upper and lower
    xupper = x[n4 * 3:]
    yupper = y[n4 * 3:]
    xlower = x[:n4]
    xlower = xlower[::-1]
    ylower = y[:n4]
    ylower = ylower[::-1]
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
        # find the 2 closest points with the divergence to the distance 2r
        ds.idx_closest[i] = dist[i, :].argmin()
        ds.dist_closest[i] = np.abs(dist[i][int(ds.idx_closest[i])] - r * 2)

    # extract idx for lower and upper surface
    idx_low = int(ds.dist_closest.idxmin())
    idx_up = int(ds.idx_closest[idx_low])

    # cut everything behind the index
    ds.xlower[ds.xlower.index.values.astype(int) > idx_low] = np.nan
    ds.ylower[ds.ylower.index.values.astype(int) > idx_low] = np.nan
    ds.xupper[ds.xupper.index.values.astype(int) > idx_up] = np.nan
    ds.yupper[ds.yupper.index.values.astype(int) > idx_up] = np.nan

    # create a half-circular-esque trailing edge
    xc_mid = ds.xlower[idx_low] + (ds.xupper[idx_up] - ds.xlower[idx_low]) / 2
    yc_mid = ds.ylower[idx_low] + (ds.yupper[idx_up] - ds.ylower[idx_low]) / 2

    # add circles to existing arrays in the df and filling up the NaNs
    ds.xupper, ds.yupper = shape_circle('up', r, [xc_mid, yc_mid], [ds.xupper, ds.yupper], idx_up)
    ds.xlower, ds.ylower = shape_circle('low', r, [xc_mid, yc_mid], [ds.xlower, ds.ylower], idx_low)

    # update original x and y
    x[n4 * 3:] = ds.xupper
    y[n4 * 3:] = ds.yupper
    x[:n4] = ds.xlower[::-1]
    y[:n4] = ds.ylower[::-1]

    # plt.plot(ds.xupper, ds.yupper)
    # plt.plot(ds.xlower, ds.ylower)
    # plt.plot(ds.xlower[idx_low], ds.ylower[idx_low], 'x')
    # plt.plot(ds.xupper[idx_up], ds.yupper[idx_up], 'x')
    # plt.plot(xc_mid, yc_mid, 'x')
    # xcamber = camberline[200:, 0]
    # ycamber = camberline[200:, 1]
    # plt.plot(xcamber, ycamber, '--')
    #
    # plt.plot(ds.xupper, ds.yupper, 'x')
    # plt.plot(ds.xlower, ds.ylower, 'x')
    # plt.axis('equal')
    #
    # plt.show()

    return x, y

#
#
# # simple design rule after MCGlumphy
# def sdr(beta1, sigma, df):
#     beta1_0 = 0
#     fun = lambda x: - df + (1 - (np.cos(beta1) / np.cos(x))) + (
#             np.cos(beta1) * (np.tan(beta1) - np.tan(x)) / (2 * sigma))
#     beta2 = optimize.fsolve(fun, beta1_0)
#
#     return beta2[0]
#
#
# def naca65gen(beta1, beta2, sigma_t, rth_t):
#     beta1 = np.rad2deg(beta1)
#     beta2 = np.rad2deg(beta2)
#     # formfactor
#     k_sh = .9
#
#     # formfactor incidence for relative profile thickness
#     q = .28 / rth_t ** .3
#     k_tinc = (10 * rth_t) ** q
#
#     # formfactor deviation for relative profile thickness
#     k_tdev = 6.25 * rth_t + 37.5 * rth_t ** 2
#
#     # zero chamber incidence- and deviation angle for (t/c = .1 = 10%)
#     # zero chamber incidence
#     p = .914 + sigma_t ** 3 / 160
#     inc0_design_10 = beta1 ** p / (5 + 46 * np.exp(-2.3 * sigma_t)) - .1 * sigma_t ** 3 * np.exp((beta1 - 70) / 4)
#
#     # zero chamber deviation
#     dev0_design_10 = .01 * sigma_t * beta1 + (.74 * sigma_t ** 1.9 + 3 * sigma_t) * (beta1 / 90) ** (
#             1.67 + 1.09 * sigma_t)
#
#     # fit angle for thickness influence (?)
#     incthick = k_sh * k_tinc * inc0_design_10
#     devthick = k_sh * k_tdev * dev0_design_10
#
#     # slope factors for profile camber
#     # slope factor incidence
#     n = 0.025 * sigma_t - 0.06 - (beta1 / 90) ** (1 + 1.2 * sigma_t) / (1.5 + 0.43 * sigma_t)
#
#     # slope factor deviation
#     m = (0.17 - 3.33e-4 * beta1 + 3.33e-5 * beta1 ** 2) / sigma_t ** (0.9625 - 0.17e-2 * beta1 - 0.85e-6 * beta1 ** 3)
#
#     # metal angle (?)
#     theta = ((beta1 - beta2) + devthick - incthick) / (1 - m + n);
#     inc_design = incthick + n * theta  # design incidence
#     dev_design = devthick + m * theta  # design deviation
#     bia = beta1 - inc_design  # Blade Inlet Angle
#     boa = beta2 - dev_design  # Blade Outlet Angle
#     lambd = (bia + boa) / 2;
#
#     return np.deg2rad(theta[0]), np.deg2rad(lambd[0])
