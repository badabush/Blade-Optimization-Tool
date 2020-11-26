import numpy as np
import pandas as pd
import random
from pathlib import Path
from matplotlib import pyplot as plt
from matplotlib import tri
from scipy.stats import gaussian_kde
from shutil import copy
import os
import re
import datetime


def _random(min, max, digits):
    """
    Random float between min and max, rounded to input digits.
    """

    return np.round(random.uniform(min, max), digits)





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
        ds = pd.DataFrame(res, columns=["pp", "ao", "omega", "beta", "cp", "fitness"])
        f.close()
        return ds


def plotDeapResult(file, logdir):
    ds = readLog(file)
    # plots for PP and AO over time
    fig, ax = plt.subplots(2, 1, sharex=True, figsize=(10, 8))
    ax[0].plot(ds.pp, label="PP")
    ax[0].legend()
    ax[0].set_ylabel("Percent Pitch [-]")

    ax[1].plot(ds.ao, label="AO")
    ax[1].set_xlabel("Iteration")
    ax[1].set_ylabel("Axial Overlap [-]")
    ax[1].legend()
    fig.savefig(Path(logdir + "/pp_ao_time.png"))

    #
    fig, ax = plt.subplots(3, 2, figsize=(10, 8), sharex='col', sharey='row')
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
            if col == 0:
                ax[row, col].set_ylabel(ds.columns[2 + row])
            if row == 2:
                ax[row, col].set_xlabel(ds.columns[col])

    fig.savefig(Path(logdir + "/gene_output_density.png"))

    # contour plot
    npts = len(ds.omega)
    ngridx = 5 * len(ds.omega)
    ngridy = 5 * len(ds.omega)

    # npts = len(ds.omega)
    ngrid = len(ds.pp)
    x = ds.ao
    y = ds.pp
    z = ds.omega

    fig, (ax1) = plt.subplots(nrows=1, figsize=(10, 8))

    xi = np.linspace(min(ds.ao) - 0.05, max(ds.ao) + 0.05, ngridx)
    yi = np.linspace(min(ds.pp) - 0.005, max(ds.pp) + 0.05, ngridy)

    triang = tri.Triangulation(x, y)

    interpolator_1 = tri.LinearTriInterpolator(triang, z)  # der kubische läuft irgendwie nicht...mh
    # interpolator_1 = tri.CubicTriInterpolator(triang, z)  # der kubische läuft irgendwie nicht...mh
    Xi, Yi = np.meshgrid(xi, yi)
    zi = interpolator_1(Xi, Yi)

    cntr1 = ax1.contourf(xi, yi, zi, levels=14, cmap="RdBu_r")

    fig.colorbar(cntr1, ax=ax1)
    ax1.scatter(x, y, facecolors='w', alpha=0.5, edgecolors='k', s=50)
    ax1.set(xlim=(min(ds.ao), max(ds.ao)), ylim=(min(ds.pp), max(ds.pp)))

    plt.subplots_adjust(hspace=0.5)
    # plt.show()
    ax1.set_xlabel('Axial Overlap [-]')
    ax1.set_ylabel('Percent Pitch [-]')
    ax1.set_title('Omega')
    fig.savefig(Path(logdir + "/pp_ao_omega_contour.png"))
    # plt.show()
    pass

def deapCleanupHandle():
    dtime = datetime.datetime.now().strftime("%d-%m-%Y_%H.%M.%S")
    logfile = Path.cwd() / "debug.log"
    os.mkdir(os.path.join(Path.cwd() / "log/", dtime))
    # copy log file to newly created folder
    copy(logfile, os.path.join(Path.cwd() / "log", dtime))
    # delete original log file
    plotDeapResult(logfile, os.path.join(Path.cwd() / "log", dtime))
    os.remove(logfile)

if __name__ == '__main__':
    deapCleanupHandle()
