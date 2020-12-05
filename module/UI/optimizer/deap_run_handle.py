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
from module.optimizer.genetic_algorithm.deaptools import _random, deapCleanupHandle


class DeapRunHandler:
    def ga_run(self):
        # min / max, fixed(bool)
        self.dp_genes = np.array([
            [0.9177, 0.9177, 1, "pp"],  # PP
            [0.0271, 0.0271, 1, "ao"],  # AO
            [0.43, 0.43, 1, "div"],  # division
            [18., 18., 1, "alph1"],  # alpha1
            [23., 23., 1, "alph2"],  # alpha2
            [23., 23., 1, "lambd"],  # lambd
            [0.0477, 0.0477, 1, "th"],  # thickness
            [0.4, 0.4, 1, "xmaxth"],  # xmaxth
            [0.35, 0.45, 0, "xmax_camber1"],  # xmaxcamber1
            [0.35, 0.45, 0, "xmax_camber2"],  # xmaxcamber2
            [0.01, 0.01, 1, "leth"],  # LE thickness
            [0.01, 0.01, 1, "teth"]  # TE thickness
        ])
        self.beta = [np.deg2rad(17)]
        # init logs
        log_format = ("[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s")
        self.logfile = datetime.datetime.now().strftime("%d-%m-%y_%H-%M-%S") + '.log'
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
        #FIXME
        self.df = pd.DataFrame(columns=['xmax_camb1', 'xmax_camb2', 'beta', 'omega', 'cp', 'fitness', 'generation'])
        self.pointer_df = 0
        # init plot
        self.optifig_deap = OptimPlotDEAP(self, width=8, height=10)
        toolbar = NavigationToolbar(self.optifig_deap, self)
        centralwidget2 = self.optimfig_widget_2
        vbl = QtGui.QVBoxLayout(centralwidget2)
        vbl.addWidget(toolbar)
        vbl.addWidget(self.optifig_deap)

        # IND_SIZE = genes[np.where(genes[:, 2] == 0)].size  # number of non-fixed genes
        self.dp_IND_SIZE = self.dp_genes.shape[0]
        self.dp_POP_SIZE = 30
        self.dp_CXPB, self.dp_MUTPB = .5, .2  # crossover probability, mutation probability

        # Creator
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        # Toolbox
        self.toolbox = base.Toolbox()

        # Attribute generator
        list(self.toolbox.register("attr_%s" % i[3], _random, float(i[0]), float(i[1]), 4) for i in self.dp_genes)

        # self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_item, n=IND_SIZE)
        self.toolbox.register("individual", tools.initCycle, creator.Individual,
                              (self.toolbox.attr_pp, self.toolbox.attr_ao, self.toolbox.attr_div,
                               self.toolbox.attr_alph1, self.toolbox.attr_alph2, self.toolbox.attr_lambd,
                               self.toolbox.attr_th, self.toolbox.attr_xmaxth,
                               self.toolbox.attr_xmax_camber1, self.toolbox.attr_xmax_camber2,
                               self.toolbox.attr_leth, self.toolbox.attr_teth), n=1)

        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        self.toolbox.register("evaluate", self.evalEngine)
        # self.toolbox.decorate("evaluate", tools.DeltaPenality(self.feasible, 3.0, self.distance))

        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", self.mutRestricted, indpb=.3)
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

    def evalEngine(self, individual):
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
        # print("PP: " + str(individual[0]))
        # print("AO: " + str(individual[1]))

        self.ds1['xmax_camber'] = individual[8]
        self.ds2['xmax_camber'] = individual[9]

        print("xmaxcamb blade1: {0}, xmaxcamb blade2: {1}".format(individual[8], individual[9]))

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
        new_row = {'xmax_camb1': individual[8], 'xmax_camb2': individual[9], 'beta': np.rad2deg(self.beta[-1]), 'omega': self.omega[-1],
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
            omega = 0
        return omega,

    def mutRestricted(self, individual, indpb):
        """
        Custom Mutation rule for keeping the genes in range.
        """

        for i, gene in enumerate(self.dp_genes):
            if random.random() < indpb:
                individual[i] = _random(float(gene[0]), float(gene[1]), 4)
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
            ind.fitness.values = fit
            try:
                self.df.iloc[idx + self.pointer_df].fitness = fit[0]
                self.df.iloc[idx + self.pointer_df].generation = g
                # FIXME
                self.logger.info(
                    "xmax_camb1:{0} ,xmax_camb2:{1} ,Omega:{2}, Beta:{3}, Cp:{4}, Fitness:{5}".format(
                        # self.df.iloc[idx + self.pointer_df].PP,
                        # self.df.iloc[idx + self.pointer_df].AO,
                        self.df.iloc[idx + self.pointer_df].xmax_camb1,
                        self.df.iloc[idx + self.pointer_df].xmax_camb2,
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
        while min(fits) > 0 and g < 100:
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
                    match_idx = np.where((self.df.xmax_camb1 == child[8]) & (self.df.xmax_camb2 == child[9]))
                    # assures that match_idx is scalar
                    match = self.df.loc[np.min(match_idx)]
                    # FIXME
                    # put winners in log (note: no extra entry in df)
                    # self.logger.info(
                    #     "PP: {0} , AO:{1} , Omega:{2}, Beta:{3}, Cp:{4}, Fitness:{5}".format(
                    #         match.PP, match.AO, match.omega, match.beta, match.cp, match.fitness
                    #     ))
                    self.logger.info(
                        "xmax_camb1: {0} , xmax_camb2:{1} , Omega:{2}, Beta:{3}, Cp:{4}, Fitness:{5}".format(
                            match.xmax_camb1, match.xmax_camb2, match.omega, match.beta, match.cp, match.fitness
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
            # idx needs to be reset in case no mutation or cx happened (for pointer_df +idx)
            for idx, (ind, fit) in enumerate(zip(invalid_ind, fitnesses)):
                # new fitness values evaluation begins
                ind.fitness.values = fit
                try:
                    print("inloop fitness:{0}".format(fit[0]))
                    self.df.iloc[idx + self.pointer_df].fitness = fit[0]
                    self.df.iloc[idx + self.pointer_df].generation = g
                    #FIXME
                    self.logger.info(
                        # "PP: {0} , AO:{1} , Omega:{2}, Beta:{3}, Cp:{4}, Fitness:{5}".format(
                        "xmax_camb1: {0} , xmax_camb2:{1} , Omega:{2}, Beta:{3}, Cp:{4}, Fitness:{5}".format(
                            # self.df.iloc[idx + self.pointer_df].PP,
                            # self.df.iloc[idx + self.pointer_df].AO,
                            self.df.iloc[idx + self.pointer_df].xmax_camb1,
                            self.df.iloc[idx + self.pointer_df].xmax_camb2,
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
                ds_len = self.df.where(self.df.generation == g).shape[0]
                self.logger.info("Population size: {0}".format(ds_len))
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

            # break loop when omega of last 5 generations didn't change
            if (g > 5):
                if np.sum(np.gradient(np.array([np.round(minlist[i], 8) for i in range(g - 5, g)]))):
                    self.logger.info("Omega didn't change for 5 Generations, breaking loop.")
                    break

        print("-- End of (successful) evolution --")

        best_ind = tools.selBest(pop, 1)[0]
        print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
        self.logger.info("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))

        # create dir and save plots of results to it. Move debug.log to folder and delete original.
        deapCleanupHandle(self.logfile)

        # plt.plot(minlist)
        # plt.show()
        # pass
