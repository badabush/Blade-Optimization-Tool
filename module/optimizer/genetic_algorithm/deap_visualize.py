import datetime
import os
from pathlib import Path
from shutil import copy
from configparser import ConfigParser

import pandas as pd
import numpy as np

from optimizer.mail.mail_script import deapMail
from optimizer.genetic_algorithm.plot.plot_feature_time import feature_time
from optimizer.genetic_algorithm.plot.plot_feature_density import feature_density
from optimizer.genetic_algorithm.plot.plot_contour import contour2
from optimizer.genetic_algorithm.plot.plot_blades import deap_blade
from optimizer.genetic_algorithm.plot.plot_scatter_matrix import scatter_matrix
from optimizer.genetic_algorithm.plot.plot_threepoint import three_point
from optimizer.genetic_algorithm.plot.plot_fitness_generation import fitness_generation, fitness_generation_scatter
from optimizer.genetic_algorithm.plot.plot_camber_thickness import distributions


class DeapVisualize:
    def __init__(self, logname, testrun=False, custom_message=""):

        # read config files
        mail_configfile = Path.cwd() / "config/mailinglist.ini"
        dtime = datetime.datetime.now().strftime("%d-%m-%Y_%H.%M.%S")
        self.logfile = Path.cwd() / logname
        if not testrun:
            path = os.path.join(Path.cwd().parent / "log/processed", dtime)
        else:
            path = os.path.join(Path.cwd().parent / "log/processed", "test_" + dtime)
        os.mkdir(path)
        # copy log file to newly created folder
        copy(self.logfile, path)

        # get reference blade beta/cp/omega from ini file
        ref_blade_config = ConfigParser()
        # ref_blade_config.read("config/reference_blade.ini")
        ref_blade_config.read("config/reference_blade2.ini")
        self.ref_blade = {"beta": float(ref_blade_config['param']['beta']),
                          "cp": float(ref_blade_config['param']['cp']),
                          "omega": float(ref_blade_config['param']['omega']),
                          "beta_lower": float(ref_blade_config['param']['beta_lower']),
                          "cp_lower": float(ref_blade_config['param']['cp_lower']),
                          "omega_lower": float(ref_blade_config['param']['omega_lower']),
                          "beta_upper": float(ref_blade_config['param']['beta_upper']),
                          "cp_upper": float(ref_blade_config['param']['cp_upper']),
                          "omega_upper": float(ref_blade_config['param']['omega_upper'])}

        self.plotDeapResult(path)
        # mail results to recipients
        if not testrun:
            attachments = []
            for item in os.listdir(Path.cwd().parent / "log/processed" / dtime):
                attachments.append(Path.cwd().parent / "log/processed" / dtime / item)
            print("Sending Mail.")
            deapMail(mail_configfile, attachments, custom_message=custom_message)

    def plotDeapResult(self, logdir):
        ds, blades, _ = self.readLog(self.logfile)
        ds_popfit = ds.loc[:,["fitness", "generation"]]
        ds_popfit = np.array([[gen, ds_popfit[ds_popfit.generation == gen].fitness.min()] for gen in ds_popfit.generation.unique()])
        mean_fitness = ds.fitness.mean()
        ds = ds[ds.fitness < mean_fitness * 2]
        ds.reset_index(inplace=True, drop=True)

        # plot camber and thickness distribution
        distributions(blades, logdir)

        # plot fitness/generation
        print("Generating Fitness/Generation plot...")
        fitness_generation(ds_popfit, logdir)
        # plot fitness/generation scatter
        print("Generating Fitness/Generation scatter plot...")
        fitness_generation_scatter(ds, ds_popfit, logdir)

        # plot 3point curve ref/best blade
        print("Generating 3point plot...")
        try:
            three_point(ds, self.ref_blade, logdir)
        except KeyError:
            print("not a 3point run.")

        # plot a feature over time
        print("Generating Feature/time plot...")
        feature_time(ds, logdir)

        # plot features over density
        print("Generating feature/density plot...")
        feature_density(ds, logdir)

        # contour(ds, logdir)
        # print("Generating contour2 plot...")
        # contour2(ds, logdir)
        #
        # print("Generating scatter plot...")
        # # scatter matrix
        # scatter_matrix(ds, logdir)

        # get default blade parameters
        print("Generating Blade plot...")
        try:
            deap_blade(blades, logdir)
        except IndexError as e:
            print(e)
            print("No blade parameters found in log file.")

        print("Done plotting.")

    @staticmethod
    def readLog(file):
        res = []
        blades = []
        popfit = []
        colnames = []
        with open(file) as f:
            lines = f.readlines()
            for line in lines:
                if "---DEAP START---" in lines:
                    # routine for detecting different runs
                    pass
                # find lines with data
                if "omega:" in line:
                    string = line.split("DEAP_info   ")[1].replace("\n", "")
                    param = string.split(",")
                    lst = []
                    col = []
                    for item in param:
                        # get column names from data row
                        if colnames.__len__() == 0:
                            col.append(item.split(":")[0].strip())
                        lst.append(float(item.split(":")[1]))
                    res.append(lst)
                    if colnames.__len__() == 0:
                        colnames = col
                # find final line of best blade
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
                            if key != "nblades" and key != "blade":
                                blade_param[key] = float(val)
                            else:
                                blade_param[key] = val
                    # FIXME
                    blade_param['npts'] = 1000
                    blade_param['thdist_pts'] = [9999]
                    blade_param['spline_pts'] = [9999]
                    # blade_param['l_chord'] = 1
                    # blade_param['selected_blade'] = 2
                    blades.append(blade_param)
                # find fitness of each generation
                if "best Fitness: " in line:
                    string = line.split("DEAP_info   ")[1].replace("\n", "")
                    pop, fit = string.split(",")
                    popfit.append([float(pop.split(": ")[1]), float(fit.split(": ")[1])])

            # Try creating pandasframe for 1point, if that doesn't work assume it was a 3point calculation.
            ds = pd.DataFrame(res, columns=colnames)

        f.close()
        return ds, blades, popfit


if __name__ == '__main__':
    msg = "FIX1: wrong reference blade parameters. \n\n"
    # DeapVisualize("test_10-02-21_19-51-14.log", True, msg)
    DeapVisualize(Path.cwd().parent / "log/raw/10-04-21_18-31-39_seed_76.log", False, msg)
