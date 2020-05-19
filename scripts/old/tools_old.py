"""
A temporary collection of small functions

"""

import pandas as pd
import numpy as np
import scipy.optimize as optimize


# simple design rule after MCGlumphy
def sdr(beta1, sigma, df):
    beta1_0 = 0
    fun = lambda x: - df + (1 - (np.cos(beta1) / np.cos(x))) + (
            np.cos(beta1) * (np.tan(beta1) - np.tan(x)) / (2 * sigma))
    beta2 = optimize.fsolve(fun, beta1_0)

    return beta2


def naca65gen(beta1, beta2, sigma_t, rth_t):

    beta1 = np.rad2deg(beta1)
    beta2 = np.rad2deg(beta2)
    # formfactor
    k_sh = .9

    # formfactor incidence for relative profile thickness
    q = .28 / rth_t ** .3
    k_tinc = (10 * rth_t) ** q

    # formfactor deviation for relative profile thickness
    k_tdev = 6.25 * rth_t + 37.5 * rth_t ** 2

    # zero chamber incidence- and deviation angle for (t/c = .1 = 10%)
    # zero chamber incidence
    p = .914 + sigma_t ** 3 / 160
    inc0_design_10 = beta1 ** p / (5 + 46 * np.exp(-2.3 * sigma_t)) - .1 * sigma_t ** 3 * np.exp((beta1 - 70) / 4)

    # zero chamber deviation
    dev0_design_10 = .01 * sigma_t * beta1 + (.74 * sigma_t ** 1.9 + 3 * sigma_t) * (beta1 / 90) ** (1.67 + 1.09 * sigma_t)

    # fit angle for thickness influence (?)
    incthick = k_sh * k_tinc * inc0_design_10
    devthick = k_sh * k_tdev * dev0_design_10

    # slope factors for profile camber
    # slope factor incidence
    n = 0.025 * sigma_t - 0.06 - (beta1 / 90) ** (1 + 1.2 * sigma_t) / (1.5 + 0.43 * sigma_t)

    # slope factor deviation
    m = (0.17 - 3.33e-4 * beta1 + 3.33e-5 * beta1 ** 2) / sigma_t ** (0.9625 - 0.17e-2 * beta1 - 0.85e-6 * beta1 ** 3)

    # metal angle (?)
    theta = ((beta1 - beta2) + devthick - incthick) / (1 - m + n);
    inc_design = incthick + n * theta  # design incidence
    dev_design = devthick + m * theta  # design deviation
    bia = beta1 - inc_design  # Blade Inlet Angle
    boa = beta2 - dev_design  # Blade Outlet Angle
    lambd = (bia + boa) / 2;

    return np.deg2rad(theta), np.deg2rad(lambd)




def FMMSpline(x, y):
    """
    PURPOSE - Compute the cubic spline with endpoint conditions chosen
    by FMM  (from the book by Forsythe,Malcolm & Moler)
    :param x:
    :param y:
    :return:
    :param yp:
    """

    n = x.size
    # x,y must be at least > 3
    assert (n) > 3
    assert (y.size) > 3

    dx = dy = delta = np.zeros(n - 1)
    dd = np.zeros(n - 2)
    dx = x[1:] - x[0:-1]
    dy = y[1:] - y[0:-1]
    delta = dy / dx
    dd = delta[1:] - delta[0:-1]
    alpha = beta = sigma = np.zeros(n)
    alpha[0] = -dx[0]
    alpha[1:-1] = 2 * (dx[0:-1] + dx[1:])
    for i in range(1, n):
        alpha[i] = alpha[i] - dx[i - 1] * dx[i - 1] / alpha[i - 1]
    alpha[-1] = -dx[-1] - dx[-1] * dx[-1] / alpha[-2]

    beta[0] = dd[1] / (x[3] - x[2]) - dd[0] / (x[1]) - dd[0] / (x[2] - x[0])
    beta[0] = beta[0] * dx[0] * dx[0] / (x[3] - x[0])

    beta[1:-1] = dd[0:n - 2]

    beta[-1] = dd[-1] / (x[-1] - x[-3]) - dd[-1] / (x[-1] - x[-4])
    beta[-1] = -beta[-1] * dx[-1] ** 2 / (x[-1] - x[-4])

    for i in range(1, n):
        beta[i] = beta[i] - dx[i - 1] * beta[i - 1] / alpha[i - 1]

    sigma = beta / alpha
    for i in range(n - 2, 0, -1):  # reverse serial loop
        sigma[i] = (beta[i] - dx[i] * sigma[i + 1]) / alpha[i]  # back substitution

    yp = np.zeros(n)
    yp[0:-1] = delta - dx * (sigma[0:-1] * 2 + sigma[1:])
    yp[-1] = yp[-2] + dx[-1] * 3 * (sigma[-1] + sigma[-2])

    return yp

def SplineZero(x, f, fp, fbar, tol):
    """
    PURPOSE - Find a value of x corresponding to a value of fbar of the cubic
    spline defined by arrays x,f,fp. f is the value of the spline at x and fp
    is the first derivative.
    NOTES - The spline is searched for an interval that crosses the specified
    value. Then Brent's method is used for finding the zero.
    :param x:
    :param f:
    :param fp:
    :param fbar:
    :param tol:
    :return:
    """

    n = x.size
    for k in range(0, n):
        if (abs(f[k]-fbar)<tol):
            xbar = x[k]

    floc = np.zeros(n)
    floc = f-fbar

    for k in range(1,n):
        if (floc[k-1]*floc[k]<0):
            exit()
    a=x[-2]
    fa = floc[-2]
    fpa = fp[-2]