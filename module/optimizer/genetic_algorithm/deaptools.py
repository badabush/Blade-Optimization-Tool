import numpy as np
import pandas as pd
import random
from pathlib import Path
from matplotlib import pyplot as plt
from scipy.stats import gaussian_kde


def _random(min, max, digits):
    """
    Random float between min and max, rounded to input digits.
    """

    return np.round(random.uniform(min, max), digits)


def mutRestricted(individual, ds_genes, indpb):
    """
    Custom Mutation rule for keeping the genes in range.
    """
    if random.random() < indpb:
        for i, gene in enumerate(ds_genes):
            individual[i] = _random(float(gene[0]), float(gene[1]), 4)
    return individual,


def readLog(file):
    res = []
    run = 0
    with open(file) as f:
        lines = f.readlines()
        for line in lines:
            if "---DEAP START---" in lines:
                # routine for detecting different runs
                pass
            if "PP: " in line:
                string = line.split("DEAP_info   ")[1].replace("\n", "")
                param = string.split(",")
                lst = []
                for item in param:
                    lst.append(float(item.split(":")[1]))
                res.append(lst)
            # print(line)
        ds = pd.DataFrame(res, columns=["pp", "ao", "omega", "beta", "cp"])
        return ds


def plotDeapResult():
    ds = readLog(Path.cwd() / "debug.log")
    fig, ax = plt.subplots(2, 1, sharex=True)
    ax[0].plot(ds.pp, label="PP")
    ax[0].legend()
    ax[0].set_ylabel("Percent Pitch [-]")

    ax[1].plot(ds.ao, label="AO")
    ax[1].set_xlabel("Iteration")
    ax[1].set_ylabel("Axial Overlap [-]")
    ax[1].legend()

    fig, ax = plt.subplots(3, 2)
    for row in range(3):
        for col in range(2):
            x = ds.iloc[:, col]
            y = ds.iloc[:, row + 2]
            # calc density
            xy = np.vstack([x, y])
            z = gaussian_kde(xy)(xy)

            # sort by density (plotted last)
            idx = z.argsort()
            x, y, z = x[idx], y[idx], z[idx]
            ax[row, col].scatter(x, y, c=z)
            ax[row, col].set_ylabel(ds.columns[2 + row])
            if row == 2:
                ax[row, col].set_xlabel(ds.columns[col])

    plt.show()
    pass


if __name__ == '__main__':
    plotDeapResult()
