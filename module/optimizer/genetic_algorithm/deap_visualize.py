import datetime
import os
from pathlib import Path
from shutil import copy

import pandas as pd

from module.optimizer.mail.mail_script import deapMail
from module.optimizer.genetic_algorithm.plot.plot_feature_time import feature_time
from module.optimizer.genetic_algorithm.plot.plot_feature_density import feature_density
from module.optimizer.genetic_algorithm.plot.plot_contour import contour, contour2
from module.optimizer.genetic_algorithm.plot.plot_blades import deap_blade
from module.optimizer.genetic_algorithm.plot.plot_scatter_matrix import scatter_matrix


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
        ds = ds[ds.omega < 0.1]
        ds.reset_index(inplace=True, drop=True)
        ds = ds[ds.fitness > 0.0]
        ds.reset_index(inplace=True, drop=True)

        # plot a feature over time
        feature_time(ds, logdir)

        # plot features over density
        feature_density(ds, logdir)

        # contour(ds, logdir)
        contour2(ds, logdir)
        # get default blade parameters
        try:
            deap_blade(blades, logdir)
        except IndexError as e:
            print(e)
            print("No blade parameters found in log file.")

        # scatter matrix
        scatter_matrix(ds, logdir)


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
    DeapVisualize("06-01-21_13-39-42.log", True)
