import random
import logging
import numpy as np
import threading
import datetime
import time
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from pyface.qt import QtGui
import pandas as pd

from deap import creator
from deap import tools
from deap import base

from module.UI.optimizer.generate_mesh_ui import MeshGenUI
from module.UI.optimizer.optimizer_plots import OptimPlotDEAP
from module.optimizer.generate_script import gen_script
from module.optimizer.optimtools import calc_xmf
from module.optimizer.genetic_algorithm.deaptools import _random, read_deap_restraints, custom_penalty
from module.optimizer.genetic_algorithm.deap_visualize import DeapVisualize
from module.UI.optimizer.deap_settings_handle import DeapSettingsHandle


class DeapRunHandler:
    def ga_run(self):
        self.testrun = False
        if self.actionTestrun.isChecked():
            self.testrun = True

        self.dp_genes = read_deap_restraints()

        # get updates from DEAP settings window
        self.deap_config_ui.get_checkbox()
        self.deap_config_ui.get_values()
        self.deap_settings = DeapSettingsHandle(self.deap_config_ui, self.dp_genes)
        self.beta = [np.deg2rad(17)]
        # init logs
        log_format = ("[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s")
        if not self.testrun:
            self.logfile = datetime.datetime.now().strftime("%d-%m-%y_%H-%M-%S") + '.log'
        else:
            self.logfile = "test_"+datetime.datetime.now().strftime("%d-%m-%y_%H-%M-%S") + '.log'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            datefmt='%d-%b-%y %H:%M:%S',
            filename=(self.logfile),
        )
        # Define logger name
        self.logger = logging.getLogger("DEAP_info")
        self.logger.info('---DEAP START---')

        # init dataframe for tracking each individuals
        # FIXME
        self.df = pd.DataFrame(
            columns=['alph11', 'alph12', 'alph21', 'alph22', 'beta', 'omega', 'cp', 'fitness', 'generation'])
        self.pointer_df = 0
        # init plot
        self.optifig_deap = OptimPlotDEAP(self, width=8, height=10)
        toolbar = NavigationToolbar(self.optifig_deap, self)
        centralwidget2 = self.optimfig_widget_2
        vbl = QtGui.QVBoxLayout(centralwidget2)
        vbl.addWidget(toolbar)
        vbl.addWidget(self.optifig_deap)

        self.dp_IND_SIZE = self.dp_genes.shape[0]
        self.dp_POP_SIZE = self.deap_config_ui.vallist['pop_size']
        self.dp_CXPB = self.deap_config_ui.vallist['cxpb']  # crossover probability
        self.dp_MUTPB = self.deap_config_ui.vallist['mutpb']  # mutation probability
        self.dp_MAX_GENERATIONS = self.deap_config_ui.vallist['max_gens']  # maximum number of generations

        # Creator
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        # Toolbox
        self.toolbox = base.Toolbox()

        # Attribute generator
        list(self.toolbox.register("attr_%s" % val[3], _random, float(val[0]), float(val[1]), int(val[2])) for val in
             self.deap_settings.attribute_generator())
        # list(self.toolbox.register("attr_%s" % i[3], _random, float(i[0]), float(i[1]), 4) for i in self.dp_IND_SIZE)
        # self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_item, n=IND_SIZE)
        self.toolbox.register(
            "individual", tools.initCycle, creator.Individual,
            (
                self.toolbox.attr_pp, self.toolbox.attr_ao, self.toolbox.attr_div,
                self.toolbox.attr_alph11, self.toolbox.attr_alph12, self.toolbox.attr_alph21, self.toolbox.attr_alph22,
                self.toolbox.attr_lambd1, self.toolbox.attr_lambd2,
                self.toolbox.attr_th1, self.toolbox.attr_th2,
                self.toolbox.attr_xmaxth1, self.toolbox.attr_xmaxth2,
                self.toolbox.attr_xmaxcamber1, self.toolbox.attr_xmaxcamber2,
                self.toolbox.attr_leth1, self.toolbox.attr_leth2,
                self.toolbox.attr_teth1, self.toolbox.attr_teth2
            ), n=1)

        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        if not self.testrun:
            self.toolbox.register("evaluate", self.eval_engine)
            # self.toolbox.decorate("evaluate", tools.DeltaPenality(self.feasible, 3.0, self.distance))
        else:
            self.toolbox.register("evaluate", self.test_eval)
            # self.toolbox.decorate("evaluate", tools.DeltaPenality(self.feasible, 3.0, self.distance))

        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", self.mut_restricted, indpb=.3)
        # self.toolbox.register("mutate", tools.mutFlipBit, indpb=.05)

        # pick 3 random individuals, fitness evaluation and selection
        self.toolbox.register("select", tools.selTournament, tournsize=3)

        # start thread for DEAP loop

        self.label_deap_status.setText("Populating.")
        t = threading.Thread(name="deap_populate", target=self.populate)
        t.start()

        self.logger.info(
            '--- POP_SIZE: {0}, CXPB: {1}, MUTPB: {2}---'.format(self.dp_POP_SIZE, self.dp_CXPB, self.dp_MUTPB))
        self.logger.info("begin population")
        # self.populate()

    def test_eval(self, individual):
        """
        generate geomTurbo
        generate .trb
        calculate blade
        calculate beta
        """
        self.outputbox("Beginning DEAP algorithm")

        print("alph1 blade1: {0}, alph2 blade1: {1}".format(individual[3], individual[4]))
        print("alph1 blade2: {0}, alph2 blade2: {1}".format(individual[5], individual[6]))

        beta = np.sum(individual[3:6])/4 + 6
        omega = np.deg2rad(beta)
        self.cp = [0, 2 * omega]
        self.beta = [beta, beta]
        self.omega = [0, omega]

        new_row = {'alph11': individual[3], 'alph12': individual[4], 'alph21': individual[5], 'alph22': individual[6],
                   'beta': self.beta[-1],
                   'omega': self.omega[-1],
                   'cp': self.cp[-1]}
        self.df = self.df.append(new_row, ignore_index=True)
        return omega,

    def eval_engine(self, individual):
        """
        generate geomTurbo
        generate .trb
        calculate blade
        calculate beta
        """
        self.outputbox("Beginning DEAP algorithm")

        # update tandem blades
        # xoffset and yoffset need to be calculated from PP and AO
        self.ds2['x_offset'] = individual[1] * self.ds1['dist_blades']  # AO
        self.ds2['y_offset'] = (1 - individual[0]) * self.ds1['dist_blades']  # PP

        # set blade 1 and 2 alphas
        self.ds1['alpha1'] = individual[3]
        self.ds1['alpha2'] = individual[4]
        self.ds2['alpha1'] = individual[5]
        self.ds2['alpha2'] = individual[6]

        print("alph1 blade1: {0}, alph2 blade1: {1}".format(individual[3], individual[4]))
        print("alph1 blade2: {0}, alph2 blade2: {1}".format(individual[5], individual[6]))

        match_idx = np.where(
            (self.df.alph11 == individual[3]) &
            (self.df.alph12 == individual[4]) &
            (self.df.alph21 == individual[5]) &
            (self.df.alph22 == individual[6]))

        # if blade was simulated before, skip numeca process
        if len(match_idx[0]) != 0:
            # assures that match_idx is scalar
            match = self.df.loc[np.min(match_idx)]
            foolist = []
            foolist.append(self.omega[-1])
            # new_row = {'PP': individual[0], 'AO': individual[1], 'beta': np.rad2deg(self.beta[-1]), 'omega': self.omega[-1],
            #            'cp': self.cp[-1]}
            # new_row = {'xmax_camb1': individual[8], 'xmax_camb2': individual[9], 'beta': np.rad2deg(self.beta[-1]),
            #            'omega': self.omega[-1],
            #            'cp': self.cp[-1]}
            new_row = {'alph11': individual[3], 'alph12': individual[4], 'alph21': individual[5],
                       'alph22': individual[6],
                       'beta': match.beta,
                       'omega': match.omega,
                       'cp': match.cp}
            self.df = self.df.append(new_row, ignore_index=True)
            print("Omega: " + str(foolist))
            # FIXME
            # self.logger.info(
            #     "PP: {0} , AO:{1} , Omega:{2}, Beta:{3}, Cp:{4}".format(individual[0], individual[1], self.omega[-1],
            #                                                             np.rad2deg(self.beta[-1]), self.cp[-1]))
            self.omega = [0, match.omega]
            self.beta = [0, match.beta]
            self.cp = [0, match.cp]
            return match.omega,


        # no dialog window if running DEAP
        self.meshgen = MeshGenUI()
        # TODO: grab paths from user somewhere
        self.meshgen.geomturbopath = "//130.149.110.81/liang/Tandem_Opti/BOT/template/autogrid/test_template.geomTurbo"
        self.meshgen.iggfolder = "//130.149.110.81/liang/Tandem_Opti/BOT/template/autogrid/"
        self.meshgen.iggname = "test_template.igg"
        # check for existing connection
        if not hasattr(self, 'sshobj'):
            self.ssh_connect()
        try:
            t = threading.Thread(name="create_meshfile", target=self.run_igg)
            t.start()
        except AttributeError:
            self.outputbox("Connecting...")

        self.outputbox("[DEAP] Waiting for igg to finish ...")
        self.igg_event.wait()
        self.outputbox("[DEAP] IGG has finished. Starting FineTurbo.")
        # self.logger.info("Mesh created successfully.")
        time.sleep(2)

        try:
            self.deap_script()
        except AttributeError:
            print("deap script crashed.")

        self.outputbox("[DEAP] Waiting for FineTurbo to finish ...")
        self.res_event.wait()
        time.sleep(2)
        # try:
        # except:
        self.beta, self.cp, self.omega = calc_xmf(self.xmf_param)
        # print("Omega: " + str(omega))

        # clear events
        self.igg_event.clear()
        self.res_event.clear()
        foolist = []
        foolist.append(self.omega[-1])
        # new_row = {'PP': individual[0], 'AO': individual[1], 'beta': np.rad2deg(self.beta[-1]), 'omega': self.omega[-1],
        #            'cp': self.cp[-1]}
        # new_row = {'xmax_camb1': individual[8], 'xmax_camb2': individual[9], 'beta': np.rad2deg(self.beta[-1]),
        #            'omega': self.omega[-1],
        #            'cp': self.cp[-1]}
        new_row = {'alph11': individual[3], 'alph12': individual[4], 'alph21': individual[5], 'alph22': individual[6],
                   'beta': np.rad2deg(self.beta[-1]),
                   'omega': self.omega[-1],
                   'cp': self.cp[-1]}
        self.df = self.df.append(new_row, ignore_index=True)
        print("Omega: " + str(foolist))
        # FIXME
        # self.logger.info(
        #     "PP: {0} , AO:{1} , Omega:{2}, Beta:{3}, Cp:{4}".format(individual[0], individual[1], self.omega[-1],
        #                                                             np.rad2deg(self.beta[-1]), self.cp[-1]))
        try:
            omega = self.omega[-1]
        except (IndexError, KeyError, ValueError) as e:
            print(e)
            omega = 9999
        return omega,

    def mut_restricted(self, individual, indpb):
        """
        Custom Mutation rule for keeping the genes in range.
        """

        for i, gene in enumerate(self.deap_settings.attribute_generator()):
            if random.random() < indpb:
                individual[i] = _random(float(gene[0]), float(gene[1]), int(gene[2]))
        return individual,

    def deap_script(self):
        """
        TODO:
        """
        # update params from control
        self.update_param()
        # refresh paths
        self.grab_paths()
        # clear plot
        self.optifig_massflow.animate_massflow({})
        # self.optifig_xmf.animate_xmf({})
        # self.optifig_xmf.clear()

        if self.box_pathtodir.text() == "":
            self.outputbox("Set Path to Project Directory first!")
            return 0
        # get display address
        self.display = "export DISPLAY=" + self.box_DISPLAY.text() + ";"

        # get node_id, number of cores, writing frequency here
        self.scriptfile = gen_script(self.paths, self.opt_param)

        # run fine131 with script
        if not hasattr(self, 'sshobj'):
            self.ssh_connect()
        if self.sshobj.transport.is_active() == False:
            self.outputbox("Could not find active session.")
            return
        try:
            self.outputbox("opening FineTurbo..")
            # sending command with display | fine version location | script + location | batch | print
            stdout = self.sshobj.send_cmd(
                self.display + "/opt/numeca/bin/fine131 -script " + "/home/HLR/" + self.paths['usr_folder'] + "/" +
                self.paths['proj_folder'] + "/BOT/py_script/" + self.scriptfile + " -batch -print")
            self.outputbox(stdout)

            # start thread to read res file
            t = threading.Thread(name='res_reader', target=self.read_res)
            t.start()

        except (TimeoutError) as e:
            # if timeout error, kill all tasks and try again
            print(e)
            self.outputbox("Fine didnt start properly. Killing tasks and retrying..")
            self.kill_loop()
            time.sleep(15)
            self.outputbox("Retrying..")
            # sending command with display | fine version location | script + location | batch | print
            stdout = self.sshobj.send_cmd(
                self.display + "/opt/numeca/bin/fine131 -script " + "/home/HLR/" + self.paths['usr_folder'] + "/" +
                self.paths['proj_folder'] + "/BOT/py_script/" + self.scriptfile + " -batch -print")
            self.outputbox(stdout)

            # start thread to read res file
            t = threading.Thread(name='res_reader', target=self.read_res)
            t.start()

    def feasible(self, _):
        """Feasibility function for beta. Returns True if feasible, False otherwise."""
        if 15 < np.rad2deg(self.beta[-1]) < 20:
            return True
        self.logger.info("Beta {0} not feasible.".format(np.round(np.rad2deg(self.beta[-1]), 3)))
        return False

    def distance(self, _):
        """Quadratic Distance function to the feasibility region."""
        return (np.rad2deg(self.beta[-1]) - 16) ** 2

    def populate(self):
        # counter generations
        g = 0
        pop = self.toolbox.population(n=self.dp_POP_SIZE)
        # evaluate population
        fitnesses = list(map(self.toolbox.evaluate, pop))

        for idx, (ind, fit) in enumerate(zip(pop, fitnesses)):
            # ind.fitness.values = fit
            # penalty on fitness when beta out of range
            fit = custom_penalty(fit, self.df.iloc[idx + self.pointer_df].beta)
            ind.fitness.values = fit
            try:
                self.df.iloc[idx + self.pointer_df].fitness = fit[0]
                self.df.iloc[idx + self.pointer_df].generation = g
                # FIXME
                self.logger.info(
                    "alph11:{0}, alph12:{1}, alph21:{2}, alph22:{3}, Omega:{4}, Beta:{5}, Cp:{6}, Fitness:{7}".format(
                        # self.df.iloc[idx + self.pointer_df].PP,
                        # self.df.iloc[idx + self.pointer_df].AO,
                        self.df.iloc[idx + self.pointer_df].alph11,
                        self.df.iloc[idx + self.pointer_df].alph12,
                        self.df.iloc[idx + self.pointer_df].alph21,
                        self.df.iloc[idx + self.pointer_df].alph22,
                        self.df.iloc[idx + self.pointer_df].omega,
                        self.df.iloc[idx + self.pointer_df].beta,
                        self.df.iloc[idx + self.pointer_df].cp,
                        self.df.iloc[idx + self.pointer_df].fitness
                    ))
            except IndexError as e:
                print(e)
                self.logger.info("Error writing individual data.")
        # extract fitnesses
        fits = [ind.fitness.values[0] for ind in pop]

        minlist = []
        # genlist = []
        while min(fits) > 0 and g < self.dp_MAX_GENERATIONS:
            # new generation
            g += 1
            self.logger.info("** Generation {0} **".format(g))
            print("-- Generation %i --" % g)
            self.label_deap_status.setText("Generation " + str(g))
            # select next generation individuals
            offspring = self.toolbox.select(pop, len(pop))
            # clone selected individual
            offspring = list(map(self.toolbox.clone, offspring))

            # put every winner of tournament into log
            for child in offspring:
                try:
                    # match_idx = np.where((self.df.PP == child[0]) & (self.df.AO == child[1]))
                    # match_idx = np.where((self.df.xmax_camb1 == child[8]) & (self.df.xmax_camb2 == child[9]))
                    match_idx = np.where(
                        (self.df.alph11 == child[3]) & (self.df.alph12 == child[4]) & (self.df.alph21 == child[5]) & (
                                self.df.alph22 == child[6]))
                    # assures that match_idx is scalar
                    match = self.df.loc[np.min(match_idx)]
                    # FIXME
                    # put winners in log (note: no extra entry in df)
                    # self.logger.info(
                    #     "PP: {0} , AO:{1} , Omega:{2}, Beta:{3}, Cp:{4}, Fitness:{5}".format(
                    #         match.PP, match.AO, match.omega, match.beta, match.cp, match.fitness
                    #     ))
                    self.logger.info(
                        "alph11:{0}, alph12:{1}, alph21:{2}, alph22:{3}, Omega:{4}, Beta:{5}, Cp:{6}, Fitness:{7}".format(
                            match.alph11, match.alph12, match.alph21, match.alph22, match.omega, match.beta, match.cp,
                            match.fitness
                        ))
                except (IndexError, KeyError, ValueError) as e:
                    print(e)
                    self.logger.info("Error writing individual data.")
            # crossover and mutations
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.dp_CXPB:
                    self.toolbox.mate(child1, child2)
                    self.logger.info("Crossover.")
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < self.dp_MUTPB:
                    self.toolbox.mutate(mutant)
                    self.logger.info("Mutation.")
                    del mutant.fitness.values

            # set df pointer to number of rows before calculation of CX/MUT
            self.pointer_df = self.df.shape[0]
            # evaluate individuals with invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]

            fitnesses = map(self.toolbox.evaluate, invalid_ind)


            for idx, (ind, fit) in enumerate(zip(invalid_ind, fitnesses)):
                # new fitness values evaluation begins
                # penalty on fitness when beta out of range
                fit = custom_penalty(fit, self.df.iloc[idx + self.pointer_df].beta)
                ind.fitness.values = fit

                try:
                    print("inloop fitness:{0}".format(fit[0]))
                    self.df.iloc[idx + self.pointer_df].fitness = fit[0]
                    self.df.iloc[idx + self.pointer_df].generation = g
                    # FIXME
                    self.logger.info(
                        # "PP: {0} , AO:{1} , Omega:{2}, Beta:{3}, Cp:{4}, Fitness:{5}".format(
                        # "xmax_camb1: {0} , xmax_camb2:{1} , Omega:{2}, Beta:{3}, Cp:{4}, Fitness:{5}".format(
                        "alph11:{0}, alph12:{1}, alph21:{2}, alph22:{3} ,Omega:{4}, Beta:{5}, Cp:{6}, Fitness:{7}".format(

                            # self.df.iloc[idx + self.pointer_df].PP,
                            # self.df.iloc[idx + self.pointer_df].AO,
                            # self.df.iloc[idx + self.pointer_df].xmax_camb1,
                            # self.df.iloc[idx + self.pointer_df].xmax_camb2,
                            self.df.iloc[idx + self.pointer_df].alph11,
                            self.df.iloc[idx + self.pointer_df].alph12,
                            self.df.iloc[idx + self.pointer_df].alph21,
                            self.df.iloc[idx + self.pointer_df].alph22,
                            self.df.iloc[idx + self.pointer_df].omega,
                            self.df.iloc[idx + self.pointer_df].beta,
                            self.df.iloc[idx + self.pointer_df].cp,
                            self.df.iloc[idx + self.pointer_df].fitness
                        ))
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

            # get total length of individuals within a generation
            try:
                ds_len = self.df[self.df.generation == g].shape[0]
                self.logger.info("Population size: {0}".format(ds_len + length))
            except (IndexError, AttributeError) as e:
                print(e)

            print("  Min %s" % min(fits))
            print("  Max %s" % max(fits))
            print("  Avg %s" % mean)
            print("  Std %s" % std)

            # plot
            minlist.append(min(fits))
            # genlist.append()
            self.optifig_deap.animate_deap(minlist)

            # FIXME:
            # break loop when omega of last 5 generations didn't change
            if (g > 5):
                if (np.sum(np.gradient(np.array([np.round(minlist[i], 5) for i in range(g - 5, g)]))) == 0):
                    self.logger.info("Omega didn't change for 5 Generations, breaking loop.")
                    break

        print("-- End of (successful) evolution --")

        best_ind = tools.selBest(pop, 1)[0]
        print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
        self.logger.info("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
        blade1_str = ""
        blade2_str = ""
        for key, val in self.ds1.items():
            # ignore pts and pts_th
            if ("pts" not in key) and ("pts_th" not in key):
                blade1_str += "{0}:{1}, ".format(key, val)
        for key, val in self.ds2.items():
            # ignore pts and pts_th
            if ("pts" not in key) and ("pts_th" not in key):
                blade2_str += "{0}:{1}, ".format(key, val)
        self.logger.info("[blade1] " + blade1_str[:-2])  # log it, remove trailing ,
        self.logger.info("[blade2] " + blade2_str[:-2])  # log it, remove trailing ,
        # create dir and save plots of results to it. Move debug.log to folder and delete original.

        DeapVisualize(self.logfile, self.testrun)

        # plt.plot(minlist)
        # plt.show()
        # pass
