import csv

import numpy as np
import pandas as pd
from scipy.special import binom


def initialize_blade_df():
    df = {
        "nblades": "tandem",
        "blade": "front",
        "th_dist_ver": 1,
        "th": 0.0,
        "alpha1": 0.0,
        "alpha2": 0.0,
        "xmax_camber": 0.0,
        "gamma_te": 0.0,
        "xmax_th": 0,
        "l_chord": 1,
        "chord_dist": 0.5,
        "lambd": 0.0,
        "th_le": 0.0,
        "th_te": 0.0,
        "npts": 1000,
        "spline_pts": [9999],
        "thdist_pts": [9999]
    }

    return df

def euclidean_dist(xy1, xy2):
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
    :type xy1: np.array
    :param xy2: list arrays of x and y values
    :type xy2: np.array
    :return: idx1, idx2, dist
    :rtype idx1: int
    :rtype idx2: int
    :rtype dist: float
    """

    dist = np.array(
        [euclidean_dist(xy1[:, i], xy2[:, j]) for i in range(0, xy1.shape[1]) for j in range(0, xy2.shape[1])])
    idx1, idx2 = np.unravel_index(dist.argmin(), (xy1.shape[1], xy2.shape[1]))
    return idx1, idx2, dist.min()


def rotate_flat(x, y):
    try:
        xmax_idx = x.idxmax()
        ymax_idx = y.idxmax()
    except AttributeError as e:
        xmax_idx = np.argmax(x)
        ymax_idx = np.argmax(y)
    xp = x[xmax_idx]
    yp = y[xmax_idx]

    rotangle = -np.arctan(yp / xp)
    X = np.cos(rotangle) * x - np.sin(rotangle) * y
    Y = np.sin(rotangle) * x + np.cos(rotangle) * y

    return X, Y, rotangle


def normalize(xy):
    X = xy.x
    Y = xy.y

    # move so left-bottom-most point is @ 0,0
    X = X - X.min()
    Y = Y - Y.min()

    X, Y, angle = rotate_flat(X, Y)

    # normalize
    xmax = X.max()
    X = X / xmax
    Y = Y / xmax

    # rotate back
    xy.x = np.cos(-angle) * X - np.sin(-angle) * Y
    xy.y = np.sin(-angle) * X + np.cos(-angle) * Y
    return xy


def load_config_file(filename):
    ds = {}
    with open(filename) as f:
        for line in f:
            item = line.strip(';\n').split(',')
            if len(item) == 1:
                continue
            elif len(item) == 2:
                ds[item[0]] = float(item[1])
            else:
                ds[item[0]] = [float(item[i]) for i in range(1, len(item))]

    return ds


class ImportExport:
    """
    Class for importing existing xyz coordinates from txt and exporting generated blade to txt (z=0).

    """

    def _import(self, file):
        """
        Import existing xyz coordinates from txt-file.
        Returns pd.DataFrame of blade.

        :param file: path + name of file to import.
        :type file: str
        :return: ds
        :rtype ds: pdDataFrame
        """
        try:
            ds = pd.read_csv(file, sep=',', header=None)
            ds.columns = ['x', 'y', 'z']
            # z will be omitted
            ds.drop(['z'], axis=1, inplace=True)
            return ds
        except FileNotFoundError as e:
            print(e)

    def _export(self, path, xy):
        """
        Export generated blade.

        :param xy: xy coordinates of blade
        :type xy: pdDataFrame
        """
        z = np.zeros(xy.shape[0])
        xyz = xy
        xyz['z'] = z
        np.savetxt(path, np.round(xyz.values, 5), fmt='%f, %f, %f')


def camber_spline(npts, xy_points):
    def bernstein(n, k):
        """Bernstein polynomial.
        """
        coeff = binom(n, k)

        def _bpoly(x):
            return coeff * x ** k * (1 - x) ** (n - k)

        return _bpoly

    def bezier(pts, npts):
        n = len(pts)
        # t = self.x
        t = x  # x-coord generation
        curve = np.zeros((npts, 2))
        for i in range(n):
            curve += np.outer(bernstein(n - 1, i)(t), pts[i])
        return curve

    npts = int(npts)
    x = .5 * (1 - np.cos(np.linspace(0, np.pi, npts)))  # x-coord generation
    # x = np.linspace(0, 1, npts)
    _x, _y = bezier(xy_points, npts).T
    return np.transpose(np.array([_x, _y]))


def cdist_from_spline(xy_spline, delta_alpha):
    """
    Generate the camber spline from spline distribution spline window.

    :param xy_spline:
    :param delta_alpha:
    :return:
    """

    x_grad = np.gradient(xy_spline[:, 0])
    y_grad = np.zeros(500)
    y_grad = np.gradient(xy_spline[:,1])
    diff = np.ones(500)
    steps = diff.size

    angle = np.cumsum(delta_alpha / steps * y_grad)

    # norm angle so it sums up to delta_alpha ([0] will be skipped anyways) | last value == del_alpha
    angle = angle / np.max(angle) * delta_alpha
    x_camber = xy_spline[:, 0]
    y_camber = np.zeros(steps)

    # doesnt work in list comprehension because it is referenced to itself?
    for i in range(1, steps):
        y_camber[i] = y_camber[i - 1] - (x_grad[i] * np.tan(angle[i]))

    # rotate
    rotangle = -np.arctan(y_camber[-1] / x_camber[-1])
    xy_camber = np.zeros_like(xy_spline)
    xy_camber[:, 0] = np.cos(rotangle) * x_camber - np.sin(rotangle) * y_camber
    xy_camber[:, 1] = np.sin(rotangle) * x_camber + np.cos(rotangle) * y_camber

    # scale
    xmax = np.max(xy_camber[:, 0])
    xy_camber[:, 0] = xy_camber[:, 0] / xmax
    xy_camber[:, 1] = xy_camber[:, 1] / xmax

    return xy_camber

def get_blade_from_csv(file_name):
    with open(file_name, 'r') as data:
        reader = csv.DictReader(data)
        ds_list = []
        for row in reader:
            # values to float
            for key in row.keys():
                try:
                    if key == "spline_pts" or key == "thdist_pts":
                        pts = []
                        string = row[key]
                        string = string.strip("[").strip("]").split("]\n [")
                        for line in string:
                            line = line.split(' ')
                            slice = list(filter(None, line))
                            slice = [float(i) for i in slice]
                            pts.append(slice)
                        row[key] = np.array(pts)
                    else:
                        row[key] = float(row[key])
                except ValueError:
                    pass
            ds_list.append(row)
        # translate OrderedDict to dict
        ds = dict(ds_list[0])
        ds1 = dict(ds_list[1])
        ds2 = dict(ds_list[2])
        return ds, ds1, ds2


class AnnulusGen:
    def __init__(self, nblades, r_inner, blade1, blade2=0):
        self.blade1 = blade1
        if blade2 == 0:
            # single blade
            pass
        else:
            # tandem blade
            self.blade2 = blade2
        self.nblades = nblades
        self.r_inner = r_inner
        self.generate()
        pass

    def generate(self):
        # generate inner circle
        t = np.linspace(0, 2 * np.pi, self.nblades)
        x = self.r_inner * np.cos(t)
        y = self.r_inner * np.sin(t)
        blade_list = pd.DataFrame(columns=["blade_%i" % (i) for i in range(self.nblades)])
        for i, c in enumerate(t):
            x_temp = np.linspace(0, 1, 100)
            y_temp = np.linspace(0, 0.01, 100)
            # x_temp = self.blade1[:, 0]# * np.cos(c) + x[i]
            # y_temp = self.blade1[:, 1]# * np.sin(c) + y[i]
            x_blade = np.cos(c) * x_temp - np.sin(c) * y_temp
            y_blade = np.sin(c) * x_temp + np.cos(c) * y_temp
            blade_list['blade_%i' % (int(i))] = np.concatenate([x_blade + x[i], y_blade + y[i]])

        return blade_list
