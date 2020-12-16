import datetime
import os
from pathlib import Path
from shutil import copy

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt, tri
from scipy.stats import gaussian_kde

from module.UI.blade.blade_plots import bladePlot
from module.optimizer.mail.mail_script import deapMail
from module.blade.bladetools import get_blade_from_csv

class DeapVisualize:
    def __init__(self, logname, testrun=False):

        # read config files
        mail_configfile = Path.cwd() / "config/mailinglist.ini"
        dtime = datetime.datetime.now().strftime("%d-%m-%Y_%H.%M.%S")
        self.logfile = Path.cwd() / logname
        if not testrun:
            path = os.path.join(Path.cwd() / "log/", dtime)
        else:
            path = os.path.join(Path.cwd() / "log/", "test_" + dtime)
        os.mkdir(path)
        # copy log file to newly created folder
        copy(self.logfile, path)

        self.plotDeapResult(path)
        # mail results to recipients
        if not testrun:
            attachments = []
            for item in os.listdir(Path.cwd() / "log" / dtime):
                attachments.append(Path.cwd() / "log" / dtime / item)
            print("Sending Mail.")
            deapMail(mail_configfile, attachments)


    def plotDeapResult(self, logdir):
        ds, blades = self.readLog(self.logfile)
        # plots for PP and AO over time
        # filter fitness < 1
        ds = ds[ds.fitness < 1]
        ds.reset_index(inplace=True, drop=True)
        ds = ds[ds.fitness > 0.0]
        ds.reset_index(inplace=True, drop=True)

        fig, ax = plt.subplots(4, 1, sharex=True, figsize=(10, 8))
        # FIXME
        ax[0].plot(ds.alph11, label="alpha 11")
        ax[0].legend()
        # ax[0].set_ylabel("Percent Pitch [-]")
        ax[0].set_ylabel("alpha1 (1) [-]")

        ax[1].plot(ds.alph12, label="alpha 12")
        ax[1].set_xlabel("Iteration")
        # ax[1].set_ylabel("Axial Overlap [-]")
        ax[1].set_ylabel("alpha2 (1) [-]")

        ax[2].plot(ds.alph21, label="alpha 21")
        ax[2].set_xlabel("Iteration")
        # ax[1].set_ylabel("Axial Overlap [-]")
        ax[2].set_ylabel("alpha1 (2) [-]")

        ax[3].plot(ds.alph22, label="alpha 22")
        ax[3].set_xlabel("Iteration")
        # ax[1].set_ylabel("Axial Overlap [-]")
        ax[3].set_ylabel("alpha2 (2) [-]")

        ax[1].legend()
        fig.savefig(Path(logdir + "/alph_time.png"))

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
        npts = len(ds.fitness)
        ngridx = 5 * len(ds.fitness)
        ngridy = 5 * len(ds.fitness)

        # npts = len(ds.omega)
        # FIXME
        ngrid = len(ds.fitness)
        x = ds.alph11
        y = ds.alph12
        z = ds.omega
        # z = ds.fitness

        fig, (ax1) = plt.subplots(nrows=1, figsize=(10, 8))

        xi = np.linspace(min(ds.alph11) - 0.05, max(ds.alph11) + 0.05, ngridx)
        yi = np.linspace(min(ds.alph12) - 0.005, max(ds.alph12) + 0.05, ngridy)

        triang = tri.Triangulation(x, y)

        interpolator_1 = tri.LinearTriInterpolator(triang, z)  # der kubische läuft irgendwie nicht...mh
        # interpolator_1 = tri.CubicTriInterpolator(triang, z)
        Xi, Yi = np.meshgrid(xi, yi)
        zi = interpolator_1(Xi, Yi)

        cntr1 = ax1.contourf(xi, yi, zi, levels=14, cmap="RdBu_r")

        fig.colorbar(cntr1, ax=ax1)
        ax1.scatter(x, y, facecolors='w', alpha=0.5, edgecolors='k', s=50)
        ax1.set(xlim=(min(ds.alph11), max(ds.alph11)), ylim=(min(ds.alph12), max(ds.alph12)))

        plt.subplots_adjust(hspace=0.5)
        # plt.show()
        # FIXME
        ax1.set_xlabel('alpha 1 (1) [-]')
        ax1.set_ylabel('alpha 2 (2) [-]')
        ax1.set_title('omega')
        fig.savefig(Path(logdir + "/xmaxcamber_fitness_contour.png"))
        # get default blade parameters

        default_blade_path = Path(os.getcwd() + "/UI/config/default_blade.csv")
        default_blade = get_blade_from_csv(default_blade_path)
        # plot blades
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            # plot best blade

            bladePlot(ax, blades[0], ds1=blades[0], ds2=blades[1], alpha=.5)

            bladePlot(ax, default_blade[0], ds1=default_blade[1], ds2=default_blade[0], alpha=1, clear=False, transparent=True)
            fig.savefig(Path(logdir + "/blades.png"))
        except IndexError as e:
            print(e)
            print("No blade parameters found in log file.")

    def readLog(self, file):
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
                    # reconstruct blade datasets
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
                    # FIXME
                    blade_param['npts'] = 1000
                    blade_param['pts'] = [9999]
                    blade_param['pts_th'] = [9999]
                    blade_param['l_chord'] = 1
                    blade_param['selected_blade'] = 2

                    blades.append(blade_param)

            # FIXME
            ds = pd.DataFrame(res, columns=["alph11", "alph12", "alph21", "alph22", "omega", "beta", "cp", "fitness"])

        f.close()
        return ds, blades


if __name__ == '__main__':
    DeapVisualize("13-12-20_16-06-30.log", True)