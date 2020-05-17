# max. thickness pos 40%
# max. camber pos 43%

# input as naca code or define thickness etc

import numpy as np
from matplotlib import pyplot as plt

from utils import FMMSpline

class BladeGen:
    """
    NACA6a(b)-cdd
    IN: a = 2nd digit (chordwise position of minimum pressiure)
        (b) = 3rd digit (range of lift coefficient in tenth above and below design lift coefficient in which favorable
         pressure gradients exists) [also written as ,b or as index in literature]
        c = 4th digit (design lift coefficient)
        d = 5th and 6th digit (max. thickness in percent)
    """

    def __init__(self, a, cl, th):
        self.a = a / 10  # chordwise extent of uniform loading 0<=a<=1
        self.c = 1
        self.cl = cl / 10  # design CL
        self.tc = th / 100  # max thickness/chord as fraction
        self.npts = 1000
        self.alpha = 0  # AOA
        # beta = np.linspace(0, np.pi, self.npts)
        # self.x = (1 - np.cos(beta)) / 2
        # # self.x = np.linspace(0, 1, self.npts)
        self.coef = [6.5718716, 0.4937629, 0.7319794, 1.9491474]  # coeficients for NACA65 profiles
        x = self.load_x()
        # ym, ymp = self.meanline(self.a, self.cl, x)  # ychord of meanline, dydx of mean line
        self.thickness(self.tc, x)
        0

    # def thickness(self):
    #     x = self.x
    #     coef = self.coef
    #
    #     th = self.th / x  # t/c
    #     # y_t = coef[0] * th + coef[1] * th ** 2 + coef[2] * th ** 3 + coef[3] * th ** 4  # thickness y coord
    #     tc = self.th / .2  # t/c
    #     y_t = tc * (0.2969 * np.sqrt(x) - 0.126 * x - 0.3516 * x ** 2 + 0.2843 * x ** 3 - 0.1015 * x ** 4)
    #
    #     return y_t

    # def naca6gen(self):
    #     """
    #     Formula from NASA report 824, NACA 6 Series
    #
    #     :return:
    #     """
    #
    #     x = self.x
    #     y_c = np.zeros(self.npts)
    #     dyc_dx = np.zeros(self.npts)
    #
    #     g = -1 / (1 - self.a) * (self.a ** 2 * (.5 * np.log(self.a) - .25) + .25)
    #     h = 1 / (1 - self.a) * (.5 * (1 - self.a) ** 2 * np.log(1 - self.a) - .25 * (1 - self.a) ** 2) + g
    #
    #     # calculate camber
    #     y_c = self.cl / (2 * np.pi * (self.a + 1)) * (
    #             1 / (1 - self.a) * (.5 * (self.a - x / self.c) ** 2 * np.log(np.abs(self.a - x / self.c))
    #                                 - .5 * (1 - x / self.c) ** 2 * np.log(1 - x / self.c) + .25 * (
    #                                         1 - x / self.c) ** 2 - .25 * (
    #                                         self.a - x / self.c) ** 2) - (x / self.c) * np.log(
    #         x / self.c) + g - h * x / self.c)  # mean camber y coordinate
    #     # y_c=c_li/(2*pi*(a+1))*(1/(1-a)*(1/2*(a-x).^2.*log(abs(a-x))-1/2*(1-x).^2.*log(1-x)+1/4*(1-x).^2-1/4*(a-x).^2)-x.*log(x)+g-h*x)
    #     # dyc_dx = self.cl / (2 * np.pi * (1 + self.a)) * (1 / (1 - self.a) * (
    #     #         (1 - x / self.c) * np.log(1 - x / self.c) - (self.a - x / self.c) * np.log(
    #     #     self.a - x / self.c)) - np.log(x / self.c) - 1 - h)
    #     dyc_dx = -(self.cl * (h + np.log(x) - (x / 2 - self.a / 2 + (np.log(1 - x) * (2 * x - 2)) / 2 + (
    #             np.log(np.abs(self.a - x)) * (2 * self.a - 2 * x)) / 2 + (
    #                                                    np.sign(self.a - x) * (self.a - x) ** 2) / (
    #                                                    2 * np.abs(self.a - x))) / (self.a - 1) + 1)) / (
    #                      2 * np.pi * (self.a + 1) * np.cos(self.alpha)) - np.tan(self.alpha)
    #     # dyc_dx=-(c_li*(h+log(x)-(x/2-a/2+(log(1-x).*(2*x-2))/2+(log(abs(a-x)).*(2*a-2*x))/2+(sign(a-x).*(a-x).^2)./(2*abs(a-x)))/(a-1)+1))/(2*pi*(a+1)*cos(alpha))-tan(alpha);    % Mean camber first derivative
    #     y_t = self.thickness()  # get y thickness from method
    #     theta = np.arctan(dyc_dx)
    #     x_upper = x - y_t * np.sin(theta)
    #     y_upper = y_c + y_t * np.cos(theta)
    #     x_lower = x + y_t * np.sin(theta)
    #     y_lower = y_c - y_t * np.cos(theta)
    #
    #     plt.figure()
    #     plt.plot(x_upper, y_upper, 'k')
    #     plt.plot(x_lower, y_lower, 'k')
    #     plt.axis('equal')
    #     plt.show()
    #     0

    def load_x(self):
        """
        Load 98 x points from list.
        :return:
        :param x: x points (98,)
        """

        x = np.array([0.0, 0.00005, 0.0001, 0.0002,
                      0.0003, 0.0004, 0.0005, 0.0006, 0.0008, 0.0010, 0.0012, 0.0014, 0.0016,
                      0.0018, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.006, 0.007, 0.008,
                      0.009, 0.01, 0.011, 0.012, 0.013, 0.014, 0.015, 0.016, 0.018, 0.02, 0.025, 0.03,
                      0.035, 0.04, 0.045, 0.05, 0.055, 0.06, 0.07, 0.08, 0.09, 0.10, 0.12,
                      0.14, 0.16, 0.18, 0.20, 0.22, 0.24, 0.26, 0.28, 0.30, 0.32, 0.34, 0.36, 0.38, 0.40,
                      0.42, 0.44, 0.46, 0.48, 0.50, 0.52, 0.54, 0.56, 0.58, 0.60, 0.62, 0.64, 0.66, 0.68,
                      0.70, 0.72, 0.74, 0.76, 0.78, 0.80, 0.82, 0.84, 0.86, 0.88, 0.90, 0.92, 0.94, 0.95,
                      0.96, 0.97, 0.975, 0.98, 0.985, 0.99, 0.995, 0.999, 1.0])
        return x

    def meanline(self, a, cl, x):
        """
        From nacax.f90 MeanLine6 subroutine. Based on "Theory of wing sections", p.74, eqn: 4-27

        :param a: chordwise extent of uniform loading [0,1]
        :param cl: design cl (lift coefficient) of the mean line
        :param x: fraction of chord
        :return:
        ym : y coord of meanline
        ymp : dydx of mean line
        """

        eps = 1e-7
        n = x.size
        ym = np.zeros(n)
        ymp = np.zeros(n)

        oma = 1 - a
        if (abs(oma) < eps):
            k = 0
            while k < n:
                xx = x[k]
                omx = 1 - xx
                if ((xx < eps) or (omx < eps)):
                    ym[k] = ymp[k] = 0
                    k += 1
                    continue
                else:
                    ym[k] = omx * np.log(omx) + xx * np.log(xx)
                    ymp[k] = np.log(omx) - np.log(xx)
                    k += 1
            ym = -ym * cl * (.25 / np.pi)
            ymp = ymp * cl * (.25 / np.pi)
        else:
            k = 0
            while k < n:
                xx = x[k]
                omx = 1 - xx
                if ((xx < eps) or (abs(omx) < eps)):
                    ym[k] = ymp[k] = 0
                    k += 1
                    continue
                if (abs(a) < eps):
                    g = -.25
                    h = -.5
                else:
                    g = -(a ** 2 * (.5 * np.log(a) - .25) + .25) / oma
                    h = g + (.5 * oma ** 2 * np.log(oma) - .25 * oma ** 2) / oma

                amx = a - xx
                if (abs(amx) < eps):
                    term1 = term1p = 0
                else:
                    term1 = amx ** 2 * (2 * np.log(abs(amx)) - 1)
                    term1p = amx * np.log(abs(amx))
                term2 = omx ** 2 * (1 - 2 * np.log(omx))
                term2p = omx * np.log(omx)

                ym[k] = .25 * (term1 + term2) / oma - xx * np.log(xx) + g - h * xx
                ymp[k] = (term1p + term2p) / oma - 1 - np.log(xx) - h
                k += 1

            ym = cl * ym / ((2 * np.pi) * (a + 1))
            ymp = cl * ymp / ((2 * np.pi) * (a + 1))

        return ym, ymp

    def thickness(self, toc, x):
        """

        :param toc: thickness/chord, fraction not percent
        :param x:

        :return:
        :param y:
        :param yp:
        :param ypp:

        """

        xt, yt = self.thickness_dist(self.tc)  # get x and y coords from thickness distribution
        sloc, xloc, yloc = self.parametrize_airfoil(xt, yt, xt, -yt)

        #fit splines to xloc vs sloc and yloc vs sloc
        xploc = FMMSpline(sloc, xloc)
        yploc = FMMSpline(sloc, yloc)

        slow = sloc[xt.size:]
        xlow = xloc[xt.size:]
        ylow = -yloc[xt.size:]
        xplow = xploc[xt.size:]
        yplow = -yploc[xt.size:]

        for k in range(0,x.size):
            0
        0
        # return y, yp, ypp

    def parametrize_airfoil(self, xupper, yupper, xlower, ylower):
        """

        :param xupper: upper x-coords from thickness dist
        :param yupper: upper y-coords from thickness dist
        :param xlower: lower x-coords from thickness dist
        :param ylower: lower y-coords from thickness dist (-yupper)

        :return:
        :param s: inscribed arc length; s=0 @ TE, along upper surface, around LE, along lower surface, back to TE
        :param x:
        :param y:
        """
        nupper = xupper.size # size of upper points
        nlower = xlower.size # size of lower points
        nn = nupper + nlower -1 # combined number of points -1 (overlap)
        s = np.zeros(nn)
        x = np.zeros(nn)
        y = np.zeros(nn)

        x[0:nupper] = xupper[::-1]
        y[0:nupper] = xupper[::-1]
        x[nupper:-1] = xlower[1:-1]
        y[nupper:-1] = ylower[1:-1]

        s[0] = 0
        for k in range(1, nn):
            s[k] = s[k-1] + np.sqrt((x[k]-x[k-1])**2 + (y[k]-y[k-1])**2)

        return s, x, y


    def LE_radius(self):
        """
        IN: toc
        :return:
        rle = yp * yp/xpp / radius LE
        """
        0

    def thickness_dist(self, tc):
        """
        Set DP for thickness distribution.

        :param tc: max value of toc
        :return:
        :param xt: x-coord of thickness dist
        :param yt: y-coord of thickness dist
        """
        # eps and psi were taken from the original nasa f90 code (21 points)
        # algorithm derived from nacax.f90 (~line 1000)
        a = 1.0  # from source code
        phi = np.linspace(0, np.pi, self.npts)

        eps = np.array(
            [0.00000, 0.01515, 0.01943, 0.01715, 0.01821, 0.02211, 0.02772, 0.03510, 0.04404, 0.05467, 0.06653,
             0.07771, 0.08614, 0.09017, 0.08982, 0.08427, 0.07368, 0.05228, 0.02939, 0.01302, 0.00000])

        psi = np.array(
            [0.17464, 0.16808, 0.15523, 0.15235, 0.15350, 0.15536, 0.15678, 0.15731, 0.15653, 0.15393, 0.14779,
             0.13680, 0.12154, 0.10353, 0.08401, 0.06385, 0.04422, 0.02590, 0.01154, 0.00289, 0.00000])
        sf = self.coef[0] * tc + self.coef[1] * tc ** 2 + self.coef[2] * tc ** 3 + self.coef[
            3] * tc ** 4  # scale factor

        eps_scaled = eps * sf
        psi_scaled = psi * sf

        """ 
        use sclaed set of eps and psi functions ot perform the conformal mapping for the circle z into the scaled 
        airfoil zfinal.
        Return the real imaginary parts as xt and yt.
        """
        z = np.array([a * np.exp(complex(psi[0], x)) for x in phi], dtype=complex)
        zprime = np.array([Z * np.exp(complex(p - psi[0], -e)) for Z, p, e in zip(z, psi, eps)], dtype=complex)
        zeta = zprime + a * a / zprime
        zfinal = (zeta[0] - zeta) / np.abs(zeta[-1] - zeta[0])
        xt = np.real(zfinal)
        yt = -np.imag(zfinal)

        return xt, yt


if __name__ == "__main__":
    # NACA65-210
    # BladeGen(5, 2, 10).naca6gen()
    BladeGen(5, 2, 10).naca6gen2()
