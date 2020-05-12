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


if __name__ == "__main__":
    # NACA65-210
    # BladeGen(5, 2, 10).naca6gen()
    BladeGen(5, 2, .0022).naca6gen()
