import numpy as np
import random


def _random(min, max, digits):
    """
    Random float between min and max, rounded to input digits.
    """

    return np.round(random.uniform(min, max), digits)

def readDeapRestraints(file):
    with open(file) as f:
        f.readlines()


if __name__ == '__main__':
    # deapCleanupHandle("10-12-20_14-38-41.log", False)
    readDeapRestraints("config/deap_restraints.ini")