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

from module.optimizer.mail.mail_script import deapMail
from module.UI.blade.blade_plots import bladePlot



def _random(min, max, digits):
    """
    Random float between min and max, rounded to input digits.
    """

    return np.round(random.uniform(min, max), digits)


def readLog(file):
    res = []
    blades = []
    with open(file) as f:
        lines = f.readlines()
        for line in lines:
            if "---DEAP START---" in lines:
                # routine for detecting different runs
                pass
            if "Omega:" in line:
                string = line.split("DEAP_info   ")[1].replace("\n", "")
                param = string.split(",")
                lst = []
                for item in param:
                    lst.append(float(item.split(":")[1]))
                res.append(lst)
            if ("[blade1] " in line) or ("[blade2] " in line):
                #reconstruct blade datasets
                blade_param = {}
                try:
                    string = line.split("[blade1] ")[1]
                except IndexError:
                    string = line.split("[blade2] ")[1]
                for elem in string.split(", "):
                    key, val = elem.split(":")
                    if val != "":
                        if key != "nblades":
                            blade_param[key] = float(val)
                        else:
                            blade_param[key] = val
                #FIXME
                blade_param['npts'] = 1000
                blade_param['pts'] = [9999]
                blade_param['pts_th'] = [9999]
                blade_param['l_chord'] = 1
                blade_param['selected_blade'] = 2

                blades.append(blade_param)

            # bladegen = BladeGen(frontend='UI', nblade=df['nblades'], th_dist_option=df['thdist_ver'],
            #                     npts=df['npts'],
            #                     alpha1=df['alpha1'], alpha2=df['alpha2'],
            #                     lambd=df['lambd'], th=df['th'], x_maxth=df['xmax_th'],
            #                     x_maxcamber=df['xmax_camber'],
            #                     l_chord=df['l_chord'], th_le=df['th_le'], th_te=df['th_te'], spline_pts=df['pts'],
            #                     thdist_points=df['pts_th'])

        # FIXME
        ds = pd.DataFrame(res, columns=["xmax_camber1", "xmax_camber2", "omega", "beta", "cp", "fitness"])


    f.close()
    return ds, blades


def plotDeapResult(file, logdir):
    ds, blades = readLog(file)
    # plots for PP and AO over time
    # filter omega > 0.1
    ds = ds[ds.omega < 0.1]
    ds.reset_index(inplace=True, drop=True)

    fig, ax = plt.subplots(2, 1, sharex=True, figsize=(10, 8))
    # FIXME
    ax[0].plot(ds.xmax_camber1, label="xmax_camber1")
    ax[0].legend()
    # ax[0].set_ylabel("Percent Pitch [-]")
    ax[0].set_ylabel("x max camber (1) [-]")

    ax[1].plot(ds.xmax_camber2, label="xmax_camber2")
    ax[1].set_xlabel("Iteration")
    # ax[1].set_ylabel("Axial Overlap [-]")
    ax[1].set_ylabel("x max camber (2) [-]")
    ax[1].legend()
    fig.savefig(Path(logdir + "/xmaxcamber_time.png"))

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
    # FIXME
    ngrid = len(ds.omega)
    x = ds.xmax_camber1
    y = ds.xmax_camber2
    z = ds.omega

    fig, (ax1) = plt.subplots(nrows=1, figsize=(10, 8))

    xi = np.linspace(min(ds.xmax_camber1) - 0.05, max(ds.xmax_camber1) + 0.05, ngridx)
    yi = np.linspace(min(ds.xmax_camber2) - 0.005, max(ds.xmax_camber2) + 0.05, ngridy)

    triang = tri.Triangulation(x, y)

    interpolator_1 = tri.LinearTriInterpolator(triang, z)  # der kubische läuft irgendwie nicht...mh
    # interpolator_1 = tri.CubicTriInterpolator(triang, z)
    Xi, Yi = np.meshgrid(xi, yi)
    zi = interpolator_1(Xi, Yi)

    cntr1 = ax1.contourf(xi, yi, zi, levels=14, cmap="RdBu_r")

    fig.colorbar(cntr1, ax=ax1)
    ax1.scatter(x, y, facecolors='w', alpha=0.5, edgecolors='k', s=50)
    ax1.set(xlim=(min(ds.xmax_camber1), max(ds.xmax_camber1)), ylim=(min(ds.xmax_camber2), max(ds.xmax_camber2)))

    plt.subplots_adjust(hspace=0.5)
    # plt.show()
    # FIXME
    ax1.set_xlabel('x max camber (1) [-]')
    ax1.set_ylabel('x max camber (2) [-]')
    ax1.set_title('Omega')
    fig.savefig(Path(logdir + "/xmaxcamber_omega_contour.png"))

    # plot blade
    fig, ax = plt.subplots(figsize=(10, 8))
    bladePlot(ax, blades[0], ds1=blades[0], ds2=blades[1])
    fig.savefig(Path(logdir + "/blades.png"))




def deapCleanupHandle(logname, mailing=True):
    # read config files
    mail_configfile = Path.cwd() / "config/mailinglist.ini"
    dtime = datetime.datetime.now().strftime("%d-%m-%Y_%H.%M.%S")
    logfile = Path.cwd() / logname
    os.mkdir(os.path.join(Path.cwd() / "log/", dtime))
    # copy log file to newly created folder
    copy(logfile, os.path.join(Path.cwd() / "log", dtime))

    plotDeapResult(logfile, os.path.join(Path.cwd() / "log", dtime))
    # mail results to recipients
    if mailing:
        attachments = []
        for item in os.listdir(Path.cwd() / "log" / dtime):
            attachments.append(Path.cwd() / "log" / dtime / item)
        deapMail(mail_configfile, attachments)
    # delete original log file
    # os.remove(logfile)


if __name__ == '__main__':
    deapCleanupHandle("04-12-20_18-05-41.log", False)
    # file = Path.cwd() / "log/04-12-2020_18.05.41_manually/04-12-20_18_05_41.log"
    # logdir = "D:/git/master-thesis/module/log/03-12-2020_07.19.36_manually"
    # plotDeapResult(file, logdir)
