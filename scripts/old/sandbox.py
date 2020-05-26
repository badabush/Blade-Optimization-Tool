"""
Sandbox to test things
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

def foo():
    r=.5
    theta = np.linspace(0, 2*np.pi, 100)
    x=r*np.cos(theta)
    y=r*np.sin(theta)
    plt.plot(x,y)
    plt.show()
    0

if __name__ == '__main__':
    foo()
