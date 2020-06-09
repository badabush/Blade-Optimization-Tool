"""
Sandbox to test things
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
from scipy import interpolate


import scipy.interpolate as si


def bspline(cv, n=100, degree=3):
    """ Calculate n samples on a bspline

        cv :      Array ov control vertices
        n  :      Number of samples to return
        degree:   Curve degree
    """
    cv = np.asarray(cv)
    count = cv.shape[0]

    # Prevent degree from exceeding count-1, otherwise splev will crash
    degree = np.clip(degree,1,count-1)

    # Calculate knot vector
    kv = np.array([0]*degree + range(count-degree+1) + [count-degree]*degree,dtype='int')

    # Calculate query range
    u = np.linspace(0,(count-degree),n)

    # Calculate result
    return np.array(si.splev(u, (kv,cv.T,degree))).T


def foo():
    colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')

    cv = np.array([[50., 25.],
                   [59., 12.],
                   [50., 10.],
                   [57., 2.],
                   [40., 4.],
                   [40., 14.]])

    plt.plot(cv[:, 0], cv[:, 1], 'o-', label='Control Points')

    for d in range(1, 5):
        p = bspline(cv, n=100, degree=d)
        x, y = p.T
        plt.plot(x, y, 'k-', label='Degree %s' % d, color=colors[d % len(colors)])

    plt.minorticks_on()
    plt.legend()
    plt.xlabel('x')
    plt.ylabel('y')
    plt.xlim(35, 70)
    plt.ylim(0, 30)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

if __name__ == '__main__':
    foo()
