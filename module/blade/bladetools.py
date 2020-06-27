import numpy as np
import pandas as pd
from scipy.special import binom
from numpy.linalg import norm
from matplotlib import pyplot as plt
import csv


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


def normalize(xy):
    # move so left-bottom-most point is @ 0,0
    xy.x = xy.x - xy.x.min()
    xy.y = xy.y - xy.y.min()
    return xy


def load_restraints(filename):
    ds = {}
    with open(filename) as f:
        for line in f:
            item = line.strip(';\n').split(',')
            try:
                ds[item[0]] = [float(item[1]), float(item[2]), float(item[3]), float(item[4])]
            except IndexError as e:
                print(e)
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

    def _export(self, xy):
        """
        Export generated blade.

        :param xy: xy coordinates of blade
        :type xy: pdDataFrame
        """
        z = np.zeros(xy.shape[0])
        xyz = xy
        xyz['z'] = z
        np.savetxt('../geo_output/xyz.txt', np.round(xyz.values, 3), fmt='%.3f, %.3f, %.3f')


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
    # x = .5 * (1 - np.cos(np.linspace(0, np.pi, npts)))  # x-coord generation
    x = np.linspace(0, 1, npts)
    _x, _y = bezier(xy_points, npts).T
    return np.transpose(np.array([_x, _y]))


def spline2camberdist(ds, delta_alpha):
    x = np.sin(np.deg2rad(45)) * ds[:,0] + np.cos(np.deg2rad(45)) * ds[:,1]
    y = -(np.cos(np.deg2rad(45)) * ds[:,0] - np.sin(np.deg2rad(45)) * ds[:,1])
    x = x/np.max(x)
    # y = np.round(y,5)

    # xgrad = np.gradient(ds[:,0])
    ystep = np.gradient(ds[:,1])
    # x = np.copy(ds[:, 0])
    # find max position
    if (np.argmax(np.round(ystep, 5))) == 0:
        xmax_idx = int(x.size/2)
    else:
        xmax_idx = np.argmax(np.round(ystep, 5))


    dalph = np.linspace(delta_alpha, 0, x.size)
    yn = np.tan(dalph*(1+y)) * x
    return x, yn


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
        # plt.plot(x, y)
        # plt.axis('equal')
        # plt.show()

        return blade_list
