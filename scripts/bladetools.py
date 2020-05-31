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
            xc = xc[::-1]  # + np.abs(xc[-1] - xy[0][idx])  # flip array
            yc = r * np.sin(theta - rot_angle) + xy_mid[1]
            yc = yc[::-1]
            yc[1:] = yc[1:]  # + np.abs(yc[0] - xy[1][idx])

            # write quarter circle into surface array, start and endpoint are left out due to overlaps
            xy[0][np.isnan(xy[0])] = xc[1:]
            xy[1][np.isnan(xy[1])] = yc[1:]
        else:
            xc = r * np.cos(theta - rot_angle) + xy_mid[0]
            xc = xc[::-1]  # + np.abs(xc[-1] - xy[0][idx])
            yc = r * np.sin(theta - rot_angle) + xy_mid[1]
            yc = yc[::-1]
            yc[1:] = yc[1:]  # - np.abs(yc[0] - xy[1][idx])

            # write quarter circle into surface array, startpoint is left out due to overlaps
            xy[0][np.isnan(xy[0])] = xc[1:]
            xy[1][np.isnan(xy[1])] = yc[1:]
    else:
        if side == 'up':
            xc = r * np.cos(theta - rot_angle) + xy_mid[0]
            xc = xc[::-1]  # - np.abs(xc[-1] - xy[0][idx])  # flip array
            yc = r * np.sin(theta - rot_angle) + xy_mid[1]
            yc = yc[::-1]  # - np.abs(yc[-1] - xy[1][idx])
            yc[1:] = yc[1:]  # + np.abs(yc[0] - xy[1][idx])

            # write quarter circle into surface array, start and endpoint are left out due to overlaps
            xy[0][np.isnan(xy[0])] = xc[1:]
            xy[1][np.isnan(xy[1])] = yc[1:]
        else:
            xc = r * np.cos(theta - rot_angle) + xy_mid[0]
            xc = xc[::-1]  # + np.abs(xc[-1] - xy[0][idx])
            yc = r * np.sin(theta - rot_angle) + xy_mid[1]
            yc = yc[::-1]
            yc[1:] = yc[1:]  # + np.abs(yc[0] - xy[1][idx])

            # write quarter circle into surface array, startpoint is left out due to overlaps
            xy[0][np.isnan(xy[0])] = xc[1:]
            xy[1][np.isnan(xy[1])] = yc[1:]

    return xy[0], xy[1]


def min_dist(xy1, xy2):
    # find closest upper surface point to each lower surface point
    x1, y1 = xy1
    x2, y2 = xy2
    dist = np.zeros([x1.size, x2.size])
    idx_closest = np.zeros(x2.size)
    for i in range(0, x1.size):
        for j in range(0, x2.size):
            dist[i][j] = euclidean_dist(x1[i], x2[j], y1[i], y2[j])

    # extract idx for lower and upper surface
    idx1, idx2 = np.unravel_index(dist.argmin(), dist.shape)
    return idx1, idx2, dist.min()


def fill_interpolate(x1, x2, xn2):
    """
    Interpolate nan values and fill into correct length
    :param x1:
    :param x2:
    :param xn2:
    :return:
    """
    diff = np.abs(x2.size - xn2.size)
    foo = np.zeros(diff)
    foo[:] = None
    xn = pd.Series(data=np.concatenate([x1.values, foo, xn2.values]))
    xn = xn.interpolate()

    return xn


def attach_circle(ds):
    def fix_clip(x, y):
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

        return x1, x2, y1, y2

    xlower1, xlower2, ylower1, ylower2 = fix_clip(ds.xlower, ds.ylower)
    xupper1, xupper2, yupper1, yupper2 = fix_clip(ds.xupper, ds.yupper)

    #poly lower
    coef = np.polyfit([xlower1.iloc[-1], xlower1.iloc[-2]], [ylower1.iloc[-1], ylower1.iloc[-2]], 1)
    polynomial_low = np.poly1d(coef)
    xn_low = xlower2.iloc[1]
    yn_low = polynomial_low(xn_low)

    # calculate angle to rotate circle
    AB = [xn_low - xlower1.iloc[-1], yn_low - ylower1.iloc[-1]]
    AC = [xlower2.iloc[1] - xlower1.iloc[-1], ylower2.iloc[1] - ylower1.iloc[-1]]
    angle_low = -np.arctan2(np.linalg.norm(np.cross(AB, AC)), np.linalg.norm(np.dot(AB, AC)))
    xlow_og, ylow_og = [xlower2.iloc[0], ylower2.iloc[0]]
    xlower2 = xlow_og + np.cos(angle_low) * (xlower2 - xlow_og) - np.sin(angle_low) * (ylower2 - ylow_og)
    ylower2 = ylow_og + np.sin(angle_low) * (xlower2 - xlow_og) + np.cos(angle_low) * (ylower2 - ylow_og)

    # fixme: fix repetition of script
    #poly upper
    coef = np.polyfit([xlower1.iloc[-1], xlower1.iloc[-2]], [ylower1.iloc[-1], ylower1.iloc[-2]], 1)
    polynomial_up = np.poly1d(coef)
    xn_up = xlower2.iloc[1]
    yn_up = polynomial_up(xn_up)

    # calculate angle to rotate circle
    AB = [xn_up - xupper1.iloc[-1], yn_up - yupper1.iloc[-1]]
    AC = [xupper2.iloc[1] - xupper1.iloc[-1], yupper2.iloc[1] - yupper1.iloc[-1]]
    angle_up = np.arctan2(np.linalg.norm(np.cross(AB, AC)), np.linalg.norm(np.dot(AB, AC)))
    xup_og, yup_og = [xupper2.iloc[0], yupper2.iloc[0]]
    # xupper2 = xup_og + np.cos(angle_up) * (xupper2 - xup_og) - np.sin(angle_up) * (yupper2 - yup_og)
    # yupper2 = yup_og + np.sin(angle_up) * (xupper2 - xup_og) + np.cos(angle_up) * (yupper2 - yup_og)

    # move lower until it collides with upper
    col = 2
    iter = 0
    while col != 0:
        iter += 1
        x0 = xlower2.iloc[1]
        y0 = polynomial_low(x0)
        xlower2 = xlower2 - np.abs(xlower2.iloc[0] - x0)
        ylower2 = ylower2 - np.abs(ylower2.iloc[0] - y0)
        idx_low, idx_up, dist = min_dist(np.array([xlower2, ylower2]), np.array([xupper2, yupper2]))
        # skip first collision
        if (dist <= 0.0002):
            col -= 1
        elif iter > 200:
            col = 0

    # cut circles @ index
    xnlower2 = xlower2.iloc[:idx_low]
    ynlower2 = ylower2.iloc[:idx_low]
    xnupper2 = xupper2.iloc[:idx_up]
    ynupper2 = yupper2.iloc[:idx_up]

    # fit back into pandas series
    ds.xlower = fill_interpolate(xlower1, xlower2, xnlower2)
    ds.ylower = fill_interpolate(ylower1, ylower2, ynlower2)

    ds.xupper = fill_interpolate(xupper1, xupper2, xnupper2)
    ds.yupper = fill_interpolate(yupper1, yupper2, ynupper2)

    ds.xupper.iloc[-1] = ds.xlower.iloc[-1]
    ds.yupper.iloc[-1] = ds.ylower.iloc[-1]
    #
    # plt.plot([xlower2.iloc[idx_low], xupper2.iloc[idx_up]], [ylower2.iloc[idx_low], yupper2.iloc[idx_up]])
    # plt.plot(xn_low, yn_low)
    # # plt.plot(xupper1, yupper1)
    # # plt.plot(xnupper2, ynupper2, 'x')
    #
    # plt.plot(ds.xupper, ds.yupper)
    # plt.plot(ds.xlower, ds.ylower)
    # # plt.plot(xnlower2, ynlower2, 'x')
    # plt.axis('equal')
    # plt.show()
    # 0

    return ds


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

    plt.plot(x, y, 'k--')
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

            if ((np.abs(j - i) > 1) and (edge == 'LE')):
                dist[i][j] = 9999
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
    r = r * 1.05
    ds.xupper, ds.yupper = shape_circle('up', edge, r, [xc_mid, yc_mid], [ds.xupper, ds.yupper], idx_up)
    ds.xlower, ds.ylower = shape_circle('low', edge, r, [xc_mid, yc_mid], [ds.xlower, ds.ylower], idx_low)


    if edge == 'TE':
        # attach_circle(ds)
        x[n4 * 3:] = ds.xupper
        y[n4 * 3:] = ds.yupper
        x[:n4] = ds.xlower[::-1]
        y[:n4] = ds.ylower[::-1]
    else:
        # fix clipping
        attach_circle(ds)
        x[n4 * 2:n4 * 3] = ds.xupper[::-1]
        y[n4 * 2:n4 * 3] = ds.yupper[::-1]
        x[n4:n4 * 2] = ds.xlower
        y[n4:n4 * 2] = ds.ylower


    xcamber = camberline[:, 0]
    ycamber = camberline[:, 1]
    plt.plot(xcamber, ycamber, '--')
    plt.plot(ds.xupper, ds.yupper)
    plt.plot(ds.xlower, ds.ylower)
    plt.axis('equal')

    plt.show()

    return x, y
