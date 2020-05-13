# max. thickness pos 40%
# max. camber pos 43%

# input as naca code or define thickness etc

import numpy as np
from matplotlib import pyplot as plt


class BladeGen:
    """
    NACA6a(b)-cdd
    IN: a = 2nd digit (chordwise position of minimum pressiure)
        (b) = 3rd digit (range of lift coefficient in tenth above and below design lift coefficient in which favorable
         pressure gradients exists) [also written as ,b or as index in literature]
        c = 4th digit (design lift coefficient)
        d = 5th and 6th digit (rel thickness)
    """

    def __init__(self, a, cl, th):
        self.a = a / 10
        self.c = 1
        self.cl = cl / 10
        self.th = th / 100
        self.npts = 1000
        self.alpha = 0  # AOA
        beta = np.linspace(0, np.pi, self.npts)
        self.x = (1 - np.cos(beta)) / 2
        # self.x = np.linspace(0, 1, self.npts)
        self.coef = [6.5718716, 0.4937629, 0.7319794, 1.9491474]  # coeficients for NACA65 profiles

    def thickness(self):
        x = self.x
        coef = self.coef

        th = self.th / x  # t/c
        # y_t = coef[0] * th + coef[1] * th ** 2 + coef[2] * th ** 3 + coef[3] * th ** 4  # thickness y coord
        tc = self.th / .2  # t/c
        y_t = tc * (0.2969 * np.sqrt(x) - 0.126 * x - 0.3516 * x ** 2 + 0.2843 * x ** 3 - 0.1015 * x ** 4)

        return y_t

    def naca6gen(self):
        """
        Formula from NASA report 824, NACA 6 Series

        :return:
        """

        x = self.x
        y_c = np.zeros(self.npts)
        dyc_dx = np.zeros(self.npts)

        g = -1 / (1 - self.a) * (self.a ** 2 * (.5 * np.log(self.a) - .25) + .25)
        h = 1 / (1 - self.a) * (.5 * (1 - self.a) ** 2 * np.log(1 - self.a) - .25 * (1 - self.a) ** 2) + g

        # calculate camber
        y_c = self.cl / (2 * np.pi * (self.a + 1)) * (
                1 / (1 - self.a) * (.5 * (self.a - x / self.c) ** 2 * np.log(np.abs(self.a - x / self.c))
                                    - .5 * (1 - x / self.c) ** 2 * np.log(1 - x / self.c) + .25 * (
                                            1 - x / self.c) ** 2 - .25 * (
                                            self.a - x / self.c) ** 2) - (x / self.c) * np.log(
            x / self.c) + g - h * x / self.c)  # mean camber y coordinate
        # y_c=c_li/(2*pi*(a+1))*(1/(1-a)*(1/2*(a-x).^2.*log(abs(a-x))-1/2*(1-x).^2.*log(1-x)+1/4*(1-x).^2-1/4*(a-x).^2)-x.*log(x)+g-h*x)
        # dyc_dx = self.cl / (2 * np.pi * (1 + self.a)) * (1 / (1 - self.a) * (
        #         (1 - x / self.c) * np.log(1 - x / self.c) - (self.a - x / self.c) * np.log(
        #     self.a - x / self.c)) - np.log(x / self.c) - 1 - h)
        dyc_dx = -(self.cl * (h + np.log(x) - (x / 2 - self.a / 2 + (np.log(1 - x) * (2 * x - 2)) / 2 + (
                np.log(np.abs(self.a - x)) * (2 * self.a - 2 * x)) / 2 + (
                                                       np.sign(self.a - x) * (self.a - x) ** 2) / (
                                                       2 * np.abs(self.a - x))) / (self.a - 1) + 1)) / (
                         2 * np.pi * (self.a + 1) * np.cos(self.alpha)) - np.tan(self.alpha)
        # dyc_dx=-(c_li*(h+log(x)-(x/2-a/2+(log(1-x).*(2*x-2))/2+(log(abs(a-x)).*(2*a-2*x))/2+(sign(a-x).*(a-x).^2)./(2*abs(a-x)))/(a-1)+1))/(2*pi*(a+1)*cos(alpha))-tan(alpha);    % Mean camber first derivative
        y_t = self.thickness()  # get y thickness from method
        theta = np.arctan(dyc_dx)
        x_upper = x - y_t * np.sin(theta)
        y_upper = y_c + y_t * np.cos(theta)
        x_lower = x + y_t * np.sin(theta)
        y_lower = y_c - y_t * np.cos(theta)

        plt.figure()
        plt.plot(x_upper, y_upper, 'k')
        plt.plot(x_lower, y_lower, 'k')
        plt.axis('equal')
        plt.show()
        0

    def naca6gen2(self):
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
        tc = self.th
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
        zprime = np.array([Z * np.exp(complex(p-psi[0], -e)) for Z, p,e in zip(z, psi, eps)], dtype=complex)
        zeta = zprime+a*a/zprime
        zfinal = (zeta[0]-zeta)/np.abs(zeta[-1]-zeta[0])
        xt = np.real(zfinal)
        yt = -np.imag(zfinal)
        0


if __name__ == "__main__":
    # NACA65-210
    # BladeGen(5, 2, 10).naca6gen()
    BladeGen(5, 2, 10).naca6gen2()
