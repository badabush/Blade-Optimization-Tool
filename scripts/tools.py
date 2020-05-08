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
    inc0_design_10 = beta1 ** p / (5 + 46 * np.exp(-2.3 * rth_t)) - .1 * rth_t ** 3 * np.exp((beta1 - 70) / 4)

    # zero chamber deviation
    dev0_design_10 = .01 * rth_t * beta1 + (.74 * rth_t ** 1.9 + 3 * rth_t) * (beta1 / 90) ** (1.67 + 1.09 * rth_t)

    # fit angle for thickness influence (?)
    incthick = k_sh * k_tinc * inc0_design_10
    devthick = k_sh * k_tdev * dev0_design_10

    # slope factors for profile camber
    # slope factor incidence
    n = 0.025 * rth_t - 0.06 - (beta1 / 90) ** (1 + 1.2 * rth_t) / (1.5 + 0.43 * rth_t)

    # slope factor deviation
    m = (0.17 - 3.33e-4 * beta1 + 3.33e-5 * beta1 ** 2) / rth_t ** (0.9625 - 0.17e-2 * beta1 - 0.85e-6 * beta1 ** 3)

    # metal angle (?)
    theta = ((beta1 - beta2) + devthick - incthick) / (1 - m + n);
    inc_design = incthick + n * theta  # design incidence
    dev_design = devthick + m * theta  # design deviation
    bia = beta1 - inc_design  # Blade Inlet Angle
    boa = beta2 - dev_design  # Blade Outlet Angle
    lambd = (bia + boa) / 2;

    return theta, lambd
