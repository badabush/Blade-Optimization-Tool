import numpy as np
import pandas as pd
from numpy.linalg import norm
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
