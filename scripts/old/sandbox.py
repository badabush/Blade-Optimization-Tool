from bladetools import camber_spline
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import fsolve

if __name__ == "__main__":
    # points = np.array([[0, 0.1, 0.5, 0.75, 1], [0, 0.5, 0.6, 0.9, 1]]).T
    points = np.array([[0, 0.25, 0.5, 0.75, 1], [0, 0.25, 0.5, 0.3, 1]]).T
    # points = np.array([[0, 0.25, 0.5, 0.75, 1], [0, 0.25, 0.5, 0.75, 1]]).T
    foo = camber_spline(1000, points)
    # dalpha = np.zeros((1000))
    # dchord = np.zeros((1000))
    # for i in range(0, 999):
    #     dalpha[i] = foo[i+1,1] - foo[i,1]
    #     dchord[i] = foo[i+1,0] - foo[i,0]
    # dadc = dalpha/dchord

    # grad = np.gradient(foo[:,0])
    # foo2 = foo[:,0] * np.tan(foo[:,1])

    foo2 = np.arctan(np.gradient(foo[:, 1]) / np.gradient(foo[:, 0]))
    # foo2 = foo2/np.max(foo2)
    x = foo[:,0]
    a = .5
    theta = np.deg2rad(30)
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
        y = fsolve(fun, y0)
        ycambertemp[i] = y

    xy_camber = np.transpose(np.array([x, ycambertemp]))


    # wolb = foo2 + np.abs(np.min(foo2))
    # wolb = wolb * -1
    # wolb = wolb + np.abs(np.min(wolb))
    # wolb = wolb / np.max(wolb)
    # kr = wolb
    plt.plot(xy_camber[:,0], xy_camber[:,1] * foo2)
    plt.plot(foo[:,0], foo2)
    plt.plot(foo[:,0], foo[:,1])
    plt.plot(points[:, 0], points[:, 1], 'x')
    # # plt.plot(foo[:, 0], kr)
    # plt.axis('equal')
    plt.show()
    pass
