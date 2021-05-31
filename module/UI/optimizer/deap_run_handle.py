import random
import logging
import numpy as np
import threading
import datetime
import time
import re
from pathlib import Path

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from pyface.qt import QtGui
import pandas as pd

from deap import creator
from deap import tools
from deap import base

from UI.optimizer.generate_mesh_ui import MeshGenUI
from UI.optimizer.optimizer_plots import OptimPlotDEAP
import optimizer.genetic_algorithm.deaptools as deaptools
from optimizer.genetic_algorithm.deap_visualize import DeapVisualize
from optimizer.optimtools import calc_xmf
from UI.optimizer.deap_settings_handle import DeapSettingsHandle


# from module.UI.optimizer.deap_run import DeapScripts


class DeapRunHandler:
    def ga_run(self, log_loaded=False):
        # constant tuning parameters for objective function
        self.log_loaded = log_loaded

        # get updates from DEAP settings window
        self.deap_config_ui.get_checkbox()
        self.deap_config_ui.get_values()
        self.dp_genes = deaptools.read_deap_restraints()
        self.deap_settings = DeapSettingsHandle(self.deap_config_ui, self.dp_genes)

        # get objective params from deap settings
        self.A, self.B, self.C = self.deap_settings.values["objective_params"]
        self.beta = [np.deg2rad(17)]

        # random seed for testing consistency of GA
        # Testrun:
        # good seed example: 65, 66, 123, 70, 71, 72
        # bad seed example: 42, 69
        # Real run:
        # good seed example: 73 (but doesnt get to global min), 74 (clean run), 75,76
        # bad seed example: 69 (blows up), 70 (very low fitness value),

        if self.deap_settings.values["random_seed"] == 0:
            seed_number = None
        else:
            seed_number = self.deap_settings.values["random_seed"]  # get seed from UI

        # load log_file if not empty
        if self.log_file:
            seed_number = int(re.search("seed_(\d)+", self.log_file).group().split("_")[-1])
            self.log_loaded = True
        self.log_idx = 0  # counter for row in loaded log file
        random.seed(seed_number)

        if self.cb_3point.isChecked():
            # refresh paths
            self.grab_paths()
            self.xmf_files, self.res_files, self.config_3point = deaptools.get_three_point_paths(self.paths)

        # counter generations
        self.generation = 0

        # initialize fit_ref as 1. During eval of ref_blade, fit/fit_ref = fit
        self.fit_ref = 1

        # init logs
        logging_path = Path.cwd().parent / "log/"
        logging_path = logging_path.__str__()
        log_format = ("[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s")
        if not self.testrun:
            if seed_number == None:
                self.logfile = logging_path + "/raw/" + datetime.datetime.now().strftime(
                    "%d-%m-%y_%H-%M-%S") + '.log'
            else:
                self.logfile = logging_path + "/raw/" + datetime.datetime.now().strftime(
                    "%d-%m-%y_%H-%M-%S_seed_{seed}".format(seed=seed_number)) + '.log'
        else:
            if seed_number == None:
                self.logfile = logging_path + "/raw/" + "test_" + datetime.datetime.now().strftime(
                    "%d-%m-%y_%H-%M-%S") + '.log'
            else:
                self.logfile = logging_path + "/raw/" + "test_" + datetime.datetime.now().strftime(
                    "%d-%m-%y_%H-%M-%S_seed_{seed}".format(seed=seed_number)) + '.log'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            datefmt='%d-%b-%y %H:%M:%S',
            filename=(self.logfile),
        )
        # Define logger name
        self.logger = logging.getLogger("DEAP_info")
        self.logger.info('--- DEAP START')
        self.logger.info('--- SOFTWARE VERSION:{version}'.format(version=self.VERSION))

        # init dataframe for tracking each individuals

        self.df = deaptools.init_deap_df(self.deap_settings.checkboxes, self.cb_3point.isChecked())
        self.pointer_df = 0
        # init plot
        self.optifig_deap = OptimPlotDEAP(self, width=8, height=10)
        toolbar = NavigationToolbar(self.optifig_deap, self)
        centralwidget2 = self.optimfig_widget_2
        vbl = QtGui.QVBoxLayout(centralwidget2)
        vbl.addWidget(toolbar)
        vbl.addWidget(self.optifig_deap)

        ### DEAP CONFIGURATION ###

        self.dp_IND_SIZE = self.dp_genes.shape[0]
        self.dp_POP_SIZE = self.deap_config_ui.vallist['pop_size']
        self.dp_CXPB = self.deap_config_ui.vallist['cxpb']  # crossover probability
        self.dp_MUTPB = self.deap_config_ui.vallist['mutpb']  # mutation probability
        self.dp_MAX_GENERATIONS = self.deap_config_ui.vallist['max_gens']  # maximum number of generations
        self.dp_BETA_CONSTRAINT = self.deap_config_ui.vallist['beta_constraint']  # beta constraint for penalty
        self.dp_BETA_CONSTRAINT_RANGE =self.deap_config_ui.vallist['beta_constraint_range']  # " range for penalty
        # Creator
        try:
            var = creator.FitnessMin
            var = creator.Individual
            del creator.FitnessMin
            del creator.Individual
            creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
            creator.create("Individual", list, fitness=creator.FitnessMin)
        except AttributeError:
            creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
            creator.create("Individual", list, fitness=creator.FitnessMin)

        # Toolbox
        self.toolbox = base.Toolbox()

        # Attribute generator
        list(self.toolbox.register("attr_%s" % val[3], deaptools._random, float(val[0]), float(val[1]), int(val[2])) for
             val in self.deap_settings.attribute_generator())
        self.toolbox.register(
            "individual", tools.initCycle, creator.Individual,
            (
                self.toolbox.attr_pp, self.toolbox.attr_ao, self.toolbox.attr_div, self.toolbox.attr_cdist,
                self.toolbox.attr_alph11, self.toolbox.attr_alph12, self.toolbox.attr_alph21, self.toolbox.attr_alph22,
                self.toolbox.attr_lambd1, self.toolbox.attr_lambd2,
                self.toolbox.attr_th1, self.toolbox.attr_th2,
                self.toolbox.attr_xmaxth1, self.toolbox.attr_xmaxth2,
                self.toolbox.attr_xmaxcamber1, self.toolbox.attr_xmaxcamber2,
                self.toolbox.attr_gamma_te1, self.toolbox.attr_gamma_te2,
                self.toolbox.attr_leth1, self.toolbox.attr_leth2,
                self.toolbox.attr_teth1, self.toolbox.attr_teth2
            ), n=1)

        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        if not self.testrun:
            self.toolbox.register("evaluate", self.eval_engine)
        else:
            self.toolbox.register("evaluate", self.test_eval)

        # using a blend with alpha=0 is identical to a cxUniform, but latter seems to be implemented differently than
        # it should be (cxUniform only swaps 2 genes)
        self.toolbox.register("mate", tools.cxBlend, alpha=0.0)
        self.toolbox.register("mutate", self.mut_restricted,
                              indpb=.1)  # TODO: indpb affects each gene, make them available in GUI

        # pick 3 random individuals, fitness evaluation and selection
        self.toolbox.register("select", tools.selTournament, tournsize=5)

        # generate header in logfile
        self.logger.info(
            '--- POP_SIZE:{popsize}, CXPB:{cxpb}, MUTPB:{mutpb}, PENALTY_FACTOR:{penalty_factor}'.format(
                popsize=self.dp_POP_SIZE, cxpb=self.dp_CXPB, mutpb=self.dp_MUTPB,
                penalty_factor=self.deap_settings.values['penalty_factor']))
        self.logger.info("--- Beta Constraint: {beta_constraint}, Beta Constraint Range: {beta_range}".format(
            beta_constraint=self.dp_BETA_CONSTRAINT, beta_range=self.dp_BETA_CONSTRAINT_RANGE))
        free_params = "".join(
            ["{param}, ".format(param=param) for (param, val) in self.deap_settings.checkboxes.items() if val == 1])
        self.logger.info("--- Free Parameters: " + free_params[:-2])
        del free_params
        if seed_number != None:
            self.logger.info("--- RANDOM SEED:{n_seed}".format(n_seed=seed_number))
        self.logger.info(
            "--- Objective function parameters: A:{A}, B:{B}, C:{C}".format(A=self.A, B=self.B, C=self.C))

        # start thread for DEAP loop
        self.label_deap_status.setText("Populating.")
        t = threading.Thread(name="deap_populate", target=self.populate, daemon=True)
        t.start()

    def test_eval(self, individual):
        """
        This method is called when the user enables test run. This will skip all connections and calculations
        in fine and instead generate some random numbers. Test runs are useful for checking GUI stability, especially
        when new implementations took place.

        """
        self.outputbox("Beginning DEAP algorithm")

        # match param names with individual value
        clean_individuals = deaptools.unravel_individual(self.deap_settings.checkboxes, self.dp_genes, individual)

        match_idx = np.where(
            (self.df.alph11 == clean_individuals.loc["alph11"].value) &
            (self.df.alph12 == clean_individuals.loc["alph12"].value) &
            (self.df.alph21 == clean_individuals.loc["alph21"].value) &
            (self.df.alph22 == clean_individuals.loc["alph22"].value))

        # look up in loaded log file
        if self.log_loaded:
            ind_row = clean_individuals.value.transpose()
            if ind_row.isin(self.log_df.iloc[self.log_idx]).all():
                print("Match!")
                new_row = deaptools.get_row(clean_individuals)
                match = self.log_df.iloc[self.log_idx]
                new_row['beta'] = match.beta
                new_row['omega'] = match.omega
                new_row['cp'] = match.cp
                new_row['generation'] = self.generation  # update generation

                self.omega = [0, match.omega]
                self.beta = [0, match.beta]
                self.cp = [0, match.cp]
                if not self.cb_3point.isChecked():
                    self.df = self.df.append(new_row, ignore_index=True)
                    return match.omega,
                else:
                    omega_lower = match.omega_lower
                    omega = match.omega
                    omega_upper = match.omega_upper
                    res = self.A * (omega_lower / self.ref_blade["omega"]) + \
                          self.B * (omega / self.ref_blade["omega"]) + \
                          self.C * (omega_upper / self.ref_blade["omega"])
                    # add 3 point parameters to new row
                    new_row['beta_lower'] = match.beta_lower
                    new_row['omega_lower'] = match.omega_lower
                    new_row['cp_lower'] = match.cp_lower
                    new_row['beta_upper'] = match.beta_upper
                    new_row['omega_upper'] = match.omega_upper
                    new_row['cp_upper'] = match.cp_upper
                    self.df = self.df.append(new_row, ignore_index=True)
                    self.log_idx += 1
                    return res,

        # if blade was simulated before, skip numeca process
        if len(match_idx[0]) != 0:
            # assures that match_idx is scalar
            match = self.df.loc[np.min(match_idx)]
            foolist = []
            foolist.append(self.omega[-1])

            new_row = deaptools.get_row(clean_individuals)
            new_row['beta'] = match.beta
            new_row['omega'] = match.omega
            new_row['cp'] = match.cp
            new_row['generation'] = self.generation  # update generation

            print("Omega: " + str(foolist))

            self.omega = [0, match.omega]
            self.beta = [0, match.beta]
            self.cp = [0, match.cp]
            if not self.cb_3point.isChecked():
                self.df = self.df.append(new_row, ignore_index=True)
                return match.omega,
            else:
                omega_lower = match.omega_lower
                omega = match.omega
                omega_upper = match.omega_upper
                res = self.A * (omega_lower / self.ref_blade["omega"]) + \
                      self.B * (omega / self.ref_blade["omega"]) + \
                      self.C * (omega_upper / self.ref_blade["omega"])
                # add 3 point parameters to new row
                new_row['beta_lower'] = match.beta_lower
                new_row['omega_lower'] = match.omega_lower
                new_row['cp_lower'] = match.cp_lower
                new_row['beta_upper'] = match.beta_upper
                new_row['omega_upper'] = match.omega_upper
                new_row['cp_upper'] = match.cp_upper
                self.df = self.df.append(new_row, ignore_index=True)
                return np.round(res, 4),

        beta = clean_individuals.value.to_numpy().sum() / 3.5
        omega = np.deg2rad(beta) / 10
        self.cp = [0, 2 * omega]
        self.beta = [beta, beta]
        self.omega = [0, omega]

        new_row = deaptools.get_row(clean_individuals)
        new_row['beta'] = self.beta[-1]
        new_row['omega'] = self.omega[-1]
        new_row['cp'] = self.cp[-1]
        new_row['generation'] = self.generation

        if not self.cb_3point.isChecked():
            self.df = self.df.append(new_row, ignore_index=True)
            return omega,
        else:
            new_row['beta_lower'] = self.beta[-1] * .9
            new_row['omega_lower'] = self.omega[-1] * 1.1
            new_row['cp_lower'] = self.cp[-1] * .9
            new_row['beta_upper'] = self.beta[-1] * 1.1
            new_row['omega_upper'] = self.omega[-1] * 1.3
            new_row['cp_upper'] = self.cp[-1] * 1.1
            res = self.A * (new_row['omega_lower'] / self.ref_blade["omega"]) + self.B * (
                    omega / self.ref_blade["omega"]) + self.C * (
                          new_row['omega_upper'] / self.ref_blade["omega"])

            self.df = self.df.append(new_row, ignore_index=True)
            return np.round(res, 4),

    def eval_engine(self, individual):
        """
        generate geomTurbo
        generate .trb
        calculate blade
        calculate beta
        """
        self.outputbox("Beginning DEAP algorithm")
        # match param names with individual value
        clean_individuals = deaptools.unravel_individual(self.deap_settings.checkboxes, self.dp_genes, individual)

        # update tandem blades
        self.ds1, self.ds2 = deaptools.update_blade_individuals(self.ds1, self.ds2, clean_individuals)
        # xoffset and yoffset need to be calculated from PP and AO
        if "AO" in clean_individuals.id.to_list():
            self.ds1['x_offset'] = clean_individuals.loc["ao"].value * self.ds1['dist_blades']  # AO
            self.ds2['x_offset'] = clean_individuals.loc["ao"].value * self.ds1['dist_blades']  # AO
        if "PP" in clean_individuals.id.to_list():
            self.ds1['y_offset'] = (1 - clean_individuals.loc["pp"].value) * self.ds1['dist_blades']  # PP
            self.ds2['y_offset'] = (1 - clean_individuals.loc["pp"].value) * self.ds1['dist_blades']  # PP

        match_idx = np.where(
            (self.df.alph11 == clean_individuals.loc["alph11"].value) &
            (self.df.alph12 == clean_individuals.loc["alph12"].value) &
            (self.df.alph21 == clean_individuals.loc["alph21"].value) &
            (self.df.alph22 == clean_individuals.loc["alph22"].value))

        # look up in loaded log file
        if self.log_loaded:
            try:
                ind_row = clean_individuals.value.transpose()
                if ind_row.isin(self.log_df.iloc[self.log_idx]).all():
                    print("Match!")
                    new_row = deaptools.get_row(clean_individuals)
                    match = self.log_df.iloc[self.log_idx]
                    new_row['beta'] = match.beta
                    new_row['omega'] = match.omega
                    new_row['cp'] = match.cp
                    new_row['generation'] = self.generation  # update generation

                    self.omega = [0, match.omega]
                    self.beta = [0, match.beta]
                    self.cp = [0, match.cp]
                    if not self.cb_3point.isChecked():
                        self.df = self.df.append(new_row, ignore_index=True)
                        return match.omega,
                    else:
                        omega_lower = match.omega_lower
                        omega = match.omega
                        omega_upper = match.omega_upper
                        res = self.A * (omega_lower / self.ref_blade["omega"]) + \
                              self.B * (omega / self.ref_blade["omega"]) + \
                              self.C * (omega_upper / self.ref_blade["omega"])
                        # add 3 point parameters to new row
                        new_row['beta_lower'] = match.beta_lower
                        new_row['omega_lower'] = match.omega_lower
                        new_row['cp_lower'] = match.cp_lower
                        new_row['beta_upper'] = match.beta_upper
                        new_row['omega_upper'] = match.omega_upper
                        new_row['cp_upper'] = match.cp_upper
                        self.df = self.df.append(new_row, ignore_index=True)
                        self.log_idx += 1
                        return res,
            except IndexError:
                pass

        # if blade was simulated before, skip numeca process
        if len(match_idx[0]) != 0:
            # assures that match_idx is scalar
            match = self.df.loc[np.min(match_idx)]
            foolist = []
            foolist.append(self.omega[-1])

            new_row = deaptools.get_row(clean_individuals)
            new_row['beta'] = match.beta
            new_row['omega'] = match.omega
            new_row['cp'] = match.cp
            new_row['generation'] = self.generation  # update generation

            print("Omega: " + str(foolist))

            self.omega = [0, match.omega]
            self.beta = [0, match.beta]
            self.cp = [0, match.cp]
            if not self.cb_3point.isChecked():
                self.df = self.df.append(new_row, ignore_index=True)
                return match.omega,
            else:
                omega_lower = match.omega_lower
                omega = match.omega
                omega_upper = match.omega_upper
                res = self.A * (omega_lower / self.ref_blade["omega"]) + \
                      self.B * (omega / self.ref_blade["omega"]) + \
                      self.C * (omega_upper / self.ref_blade["omega"])
                # add 3 point parameters to new row
                new_row['beta_lower'] = match.beta_lower
                new_row['omega_lower'] = match.omega_lower
                new_row['cp_lower'] = match.cp_lower
                new_row['beta_upper'] = match.beta_upper
                new_row['omega_upper'] = match.omega_upper
                new_row['cp_upper'] = match.cp_upper
                self.df = self.df.append(new_row, ignore_index=True)
                return res / self.fit_ref,

        # solve blade with numeca if none of the above applies
        return self.solve_blade(clean_individuals)

    def solve_blade(self, clean_individuals, refblade=False):
        # no dialog window if running DEAP
        self.meshgen = MeshGenUI()
        # TODO: grab paths from user somewhere
        self.meshgen.geomturbopath = "//130.149.110.81/liang/Tandem_Opti/BOT/template/autogrid/test_template.geomTurbo"
        self.meshgen.iggfolder = "//130.149.110.81/liang/Tandem_Opti/BOT/template/autogrid/"
        self.meshgen.iggname = "test_template.igg"
        # check for existing connection
        if not hasattr(self, 'sshobj'):
            self.ssh_connect()
        t = threading.Thread(name="create_meshfile", target=self.run_igg, daemon=True)
        t.start()
        self.outputbox("[DEAP] Waiting for igg to finish ...")
        self.igg_event.wait()
        time.sleep(5)
        self.outputbox("[DEAP] IGG has finished. Starting FineTurbo.")
        if not hasattr(self, 'sshobj'):
            self.ssh_connect()
        try:
            if not self.cb_3point.isChecked():

                self.deap_one_point()
            else:
                # self.deap_three_point()
                self.run_3point()
        except AttributeError:
            print("deap script crashed.")
        self.outputbox("[DEAP] Waiting for FineTurbo to finish ...")
        self.res_event.wait()
        time.sleep(2)
        # if calculation didn't start or ran into an error for whatever reason
        if self.res_failed_event.is_set():
            self.res_failed_event.clear()
            return 9999,
        self.beta, self.cp, self.omega = calc_xmf(self.xmf_param)
        # clear events
        self.igg_event.clear()
        self.res_event.clear()
        foolist = []
        try:
            omega = self.omega[-1]
        except IndexError:
            omega = 0
        foolist.append(omega)
        new_row = deaptools.get_row(clean_individuals)
        new_row['beta'] = np.rad2deg(self.beta[-1])
        new_row['omega'] = self.omega[-1]
        new_row['cp'] = self.cp[-1]
        print("Omega: " + str(foolist))
        try:
            omega = self.omega[-1]
        except (IndexError, KeyError, ValueError) as e:
            print(e)
            omega = 9999
        if self.cb_3point.isChecked():
            beta_lower, cp_lower, omega_lower = calc_xmf(self.xmf_param_lower)
            beta_upper, cp_upper, omega_upper = calc_xmf(self.xmf_param_upper)

            # add 3 point parameters to new row
            new_row['beta_lower'] = np.rad2deg(beta_lower[-1])
            new_row['omega_lower'] = omega_lower[-1]
            new_row['cp_lower'] = cp_lower[-1]
            new_row['beta_upper'] = np.rad2deg(beta_upper[-1])
            new_row['omega_upper'] = omega_upper[-1]
            new_row['cp_upper'] = cp_upper[-1]
            res = self.A * (omega_lower[-1] / self.ref_blade["omega"]) + self.B * (
                    omega / self.ref_blade["omega"]) + self.C * (
                          omega_upper[-1] / self.ref_blade["omega"])
            if not refblade:
                self.df = self.df.append(new_row, ignore_index=True)

            return res / self.fit_ref,

        if not refblade:
            self.df = self.df.append(new_row, ignore_index=True)
        return omega / self.fit_ref,

    def mut_restricted(self, individual, indpb):
        """
        Custom Mutation rule for keeping the genes in range.
        """
        for i, gene in enumerate(self.deap_settings.attribute_generator()):
            if random.random() < indpb:
                individual[i] = deaptools._random(float(gene[0]), float(gene[1]), int(gene[2]))
        return individual,

    def populate(self):
        # update fit_ref with the actual value from evaluation of ref_blade
        if not self.testrun:

            # TODO: take ref_fit from log if loaded
            # Run Reference Blade once
            self.outputbox("[DEAP] Running Ref_Blade through solver.")
            ref_individual = deaptools.ind_list_from_datasets(self.ds1, self.ds2, self.dp_genes)
            self.label_deap_status.setText("Generating reference blade.")

            logstr = "".join(["{key}:{val}, ".format(key=key, val=val) for key, val in
                              zip(self.dp_genes.index.to_list(), ref_individual)])
            self.logger.info("--- Reference Blade parameters: " + logstr[:-2])
            del logstr

            clean_individuals = deaptools.unravel_individual(self.deap_settings.checkboxes, self.dp_genes,
                                                             ref_individual)

            # update tandem blades
            self.ds1, self.ds2 = deaptools.update_blade_individuals(self.ds1, self.ds2, clean_individuals)
            # xoffset and yoffset need to be calculated from PP and AO
            # TODO: change reference to clean_individuals
            self.ds2['x_offset'] = ref_individual[1] * self.ds1['dist_blades']  # AO
            self.ds2['y_offset'] = (1 - ref_individual[0]) * self.ds1['dist_blades']  # PP

            # take fitref from log file if loaded, calculate otherwise
            if self.log_loaded:
                self.fit_ref = float(self.ds_log_meta["ref_fit"])
            else:
                self.fit_ref, = self.solve_blade(clean_individuals, True)

            self.outputbox("[DEAP] Updating fit_ref to {fit}".format(fit=self.fit_ref))
            del ref_individual
            self.logger.info("--- Reference Blade Fitness:{fit_ref}".format(fit_ref=np.round(self.fit_ref, 4)))
        self.logger.info("begin population")
        self.label_deap_status.setText("Populating.")

        pop = self.toolbox.population(n=self.dp_POP_SIZE)
        # evaluate population
        fitnesses = list(map(self.toolbox.evaluate, pop))

        for idx, (ind, fit) in enumerate(zip(pop, fitnesses)):
            # penalty on fitness when beta out of range
            if not fit[-1] > 9998:
                if not self.log_loaded:
                    fit = deaptools.custom_penalty(fit, self.df.iloc[idx + self.pointer_df].beta,
                                                   self.deap_settings.values['penalty_factor'],
                                                   beta_default=self.deap_settings.values['beta_constraint'],
                                                   beta_range_default=self.deap_settings.values['beta_constraint_range'])
                else:

                    if ((self.pointer_df + idx) <= self.log_df.shape[0]) and (self.log_df.shape[0] != 0):
                        fit = (self.log_df.iloc[self.pointer_df + idx].fitness,)
                    else:
                        fit = deaptools.custom_penalty(fit, self.df.iloc[idx + self.pointer_df].beta,
                                                       self.deap_settings.values['penalty_factor'],
                                                   beta_default=self.deap_settings.values['beta_constraint'],
                                                   beta_range_default=self.deap_settings.values['beta_constraint_range'])
            ind.fitness.values = fit
            try:
                self.df.iloc[idx + self.pointer_df].fitness = fit[0]
                self.df.iloc[idx + self.pointer_df].generation = self.generation
                entry = deaptools.generate_log(idx + self.pointer_df, self.df)
                self.logger.info(entry)
            except IndexError as e:
                print(e)
                self.logger.info("Error writing individual data.")

        # extract fitnesses
        fits = [ind.fitness.values[0] for ind in pop]

        minlist = []
        ngen_size = len(pop)
        while min(fits) > 0 and self.generation < self.dp_MAX_GENERATIONS:
            # new generation
            self.generation += 1
            self.logger.info("** Generation {0} **".format(self.generation))
            print("-- Generation %i --" % self.generation)
            self.label_deap_status.setText("Generation " + str(self.generation))
            # select parent individuals
            offspring = self.toolbox.select(pop, ngen_size)
            # clone selected individual
            offspring = list(map(self.toolbox.clone, offspring))

            if self.log_loaded and (self.log_idx + self.dp_POP_SIZE) < self.log_df.shape[0]:
                ### copy offspring from log df
                subset = self.log_df.iloc[self.log_idx:(self.log_idx + self.dp_POP_SIZE)].reset_index().drop(["index"],
                                                                                                             axis=1)
                for idx_child, child in enumerate(offspring):
                    for idx in range(len(child)):
                        if self.dp_genes.iloc[idx].name in subset:
                            offspring[idx_child][idx] = subset[self.dp_genes.iloc[idx].name].iloc[idx_child]
                            del child.fitness.values
            else:
                # crossover and mutations
                for (idx_cx1, child1), (idx_cx2, child2) in zip(enumerate(offspring[::2]), enumerate(offspring[1::2])):
                    # placing the delete statements here will force the GA to reevaluate all fitnesses, thus logging
                    # the whole new generation
                    del child1.fitness.values
                    del child2.fitness.values
                    if random.random() < self.dp_CXPB:
                        self.toolbox.mate(child1, child2)

                for idx_mut, mutant in enumerate(offspring):
                    # placing the delete statements here will force the GA to reevaluate all fitnesses, thus logging
                    # the whole new generation
                    del mutant.fitness.values
                    if random.random() < self.dp_MUTPB:
                        self.toolbox.mutate(mutant)

            # set df pointer to number of rows before calculation of CX/MUT
            self.pointer_df = self.df.shape[0]
            # evaluate individuals with invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]

            fitnesses = map(self.toolbox.evaluate, invalid_ind)

            for idx, (ind, fit) in enumerate(zip(invalid_ind, fitnesses)):
                # new fitness values evaluation begins
                # penalty on fitness when beta out of range

                # don't apply custom penalty when fitness is faulty
                if not fit[-1] > 9998:
                    if not self.log_loaded:
                        fit = deaptools.custom_penalty(fit, self.df.iloc[idx + self.pointer_df].beta,
                                                       self.deap_settings.values['penalty_factor'],
                                                   beta_default=self.deap_settings.values['beta_constraint'],
                                                   beta_range_default=self.deap_settings.values['beta_constraint_range'])
                    else:
                        if (self.pointer_df + idx) < self.log_df.shape[0]:
                            fit = (self.log_df.iloc[self.pointer_df + idx].fitness,)
                        else:
                            fit = deaptools.custom_penalty(fit, self.df.iloc[idx + self.pointer_df].beta,
                                                           self.deap_settings.values['penalty_factor'],
                                                   beta_default=self.deap_settings.values['beta_constraint'],
                                                   beta_range_default=self.deap_settings.values['beta_constraint_range'])
                ind.fitness.values = fit

                try:
                    self.df.iloc[idx + self.pointer_df].fitness = fit[-1]
                    self.df.iloc[idx + self.pointer_df].generation = self.generation
                    entry = deaptools.generate_log(idx + self.pointer_df, self.df)
                    self.logger.info(entry)
                except (IndexError, KeyError, ValueError) as e:
                    print(e)
            # replace entire existing population with offspring
            pop[:] = offspring

            # Gather all the fitnesses in one list and print the stats
            fits = [ind.fitness.values[0] for ind in pop]

            length = len(pop)
            mean = sum(fits) / length
            sum2 = sum(x * x for x in fits)
            std = abs(sum2 / length - mean ** 2) ** 0.5
            minfit = self.df.fitness.iloc[self.pointer_df:].min()
            # get total length of individuals within a generation
            self.logger.info("Population size: {0}, best Fitness: {1}".format(length, minfit))

            print("  Min %s" % minfit)
            print("  Max %s" % max(fits))
            print("  Avg %s" % mean)
            print("  Std %s" % std)

            # plot
            minlist.append(minfit)
            self.optifig_deap.animate_deap(minlist)
            # break loop when omega of last n generations didn't change
            n_identical_gens = 10
            if (self.generation > n_identical_gens):
                if all(np.round(x, 5) == np.round(minlist[-1], 5) for x in minlist[-n_identical_gens:]):
                    self.logger.info(
                        "Fitness didn't change for {ngens} Generations, breaking loop.".format(ngens=n_identical_gens))
                    break

        print("-- End of (successful) evolution --")

        best_ind = tools.selBest(pop, 1)[0]
        print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
        try:
            idx_best = self.df[self.df.fitness == np.min(minlist)].index[0]
            self.logger.info("Best individual: ")
            entry = deaptools.generate_log(idx_best, self.df)
            self.logger.info(entry)
        except IndexError as e:
            print(e)

        blade1_str = ""
        blade2_str = ""
        ind_best = deaptools.unravel_individual(self.deap_settings.checkboxes, self.dp_genes, best_ind)
        for key, val in self.ds1.items():
            # ignore pts and pts_th
            if ("pts" not in key) and ("pts_th" not in key):
                if key in ind_best.id.to_list():
                    val = ind_best[(ind_best.id == key) & (ind_best.blade != "2")].value.values[0]
                blade1_str += "{0}:{1}, ".format(key, val)
        for key, val in self.ds2.items():
            # ignore pts and pts_th
            if ("pts" not in key) and ("pts_th" not in key):
                if key in ind_best.id.to_list():
                    if not "chord_dist" in key:
                        val = ind_best[(ind_best.id == key) & (ind_best.blade != "1")].value.values[0]
                    else:
                        val = 1-ind_best[(ind_best.id == key) & (ind_best.blade != "1")].value.values[0]
                blade2_str += "{0}:{1}, ".format(key, val)
        self.logger.info("[blade1] " + blade1_str[:-2])  # log it, remove trailing ,
        self.logger.info("[blade2] " + blade2_str[:-2])  # log it, remove trailing ,
        # create dir and save plots of results to it. Move debug.log to folder and delete original.

        # self.testrun = True
        custom_message = ""
        if self.log_loaded:
            custom_message = "Continuation of log."
        DeapVisualize(self.logfile, self.testrun, custom_message=custom_message)
