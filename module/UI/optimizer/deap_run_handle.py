import numpy as np
import random
import threading
import paramiko
import time

from deap import creator
from deap import tools
from deap import base

from module.UI.optimizer.generate_mesh_ui import MeshGenUI
from module.optimizer.generate_script import gen_script
from module.optimizer.optimtools import calc_xmf


class DeapRunHandler:
    def ga_run(self):
        # min / max, fixed(bool)
        self.dp_genes = np.array([
            [0.85, 0.95, 0, "pp"],  # PP
            [-0.1, 0.1, 0, "ao"],  # AO
            [0.43, 0.43, 1, "div"],  # division
            [18., 18., 1, "alph1"],  # alpha1
            [23., 23., 1, "alph2"],  # alpha2
            [23., 23., 1, "lambd"],  # lambd
            [0.0477, 0.0477, 1, "th"],  # thickness
            [0.4, 0.4, 1, "xmaxth"],  # xmaxth
            [0.3742, 0.3742, 1, "xmaxch"],  # xmaxcamber
            [0.01, 0.01, 1, "leth"],  # LE thickness
            [0.01, 0.01, 1, "teth"]  # TE thickness
        ])

        # IND_SIZE = genes[np.where(genes[:, 2] == 0)].size  # number of non-fixed genes
        self.dp_IND_SIZE = self.dp_genes.shape[0]
        self.dp_POP_SIZE = 100
        self.dp_CXPB, self.dp_MUTPB = .5, .2  # crossover probability, mutation probability

        # Creator
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        # Toolbox
        self.toolbox = base.Toolbox()

        # Attribute generator
        list(self.toolbox.register("attr_%s" % i[3], random.uniform, float(i[0]), float(i[1])) for i in self.dp_genes)

        # self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_item, n=IND_SIZE)
        self.toolbox.register("individual", tools.initCycle, creator.Individual,
                              (self.toolbox.attr_pp, self.toolbox.attr_ao, self.toolbox.attr_div,
                               self.toolbox.attr_alph1, self.toolbox.attr_alph2, self.toolbox.attr_lambd,
                               self.toolbox.attr_th, self.toolbox.attr_xmaxth, self.toolbox.attr_xmaxch,
                               self.toolbox.attr_leth, self.toolbox.attr_teth), n=1)

        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        self.toolbox.register("evaluate", self.evalEngine)
        # self.toolbox.register("evaluate", benchmarks.ackley)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", self.mutRestricted, indpb=.3)
        # self.toolbox.register("mutate", tools.mutFlipBit, indpb=.05)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

        # start thread for DEAP loop

        t = threading.Thread(name="deap_populate", target=self.populate)
        t.start()

        # self.populate()

    def evalEngine(self, individual):
        """
        generate geomTurbo
        generate .trb
        calculate blade
        calculate beta
        """
        self.outputbox("Beginning DEAP algorithm")

        # update blade parameters from DEAP generation
        self.ds["PP"] = individual[0]
        self.ds["AO"] = individual[1]
        print("PP: " + str(individual[0]))
        print("AO: " + str(individual[1]))

        # self.create_meshfile(passthrough=True)

        # no dialog window if running DEAP
        self.meshgen = MeshGenUI()
        # TODO: grab paths from user somewhere
        self.meshgen.geomturbopath = "//130.149.110.81/liang/Tandem_Opti/BOT/template/autogrid/test_template.geomTurbo"
        self.meshgen.iggfolder = "//130.149.110.81/liang/Tandem_Opti/BOT/template/autogrid/"
        self.meshgen.iggname = "test_template.igg"
        # check for existing connection
        if not hasattr(self, 'sshobj'):
            self.ssh_connect()
        # try:
        #     t = threading.Thread(name="create_meshfile", target=self.run_igg)
        #     t.start()
        # except AttributeError:
        #     self.outputbox("Connecting...")

        # self.outputbox("[DEAP] Waiting for igg to finish ...")
        # self.igg_event.wait()
        # self.outputbox("[DEAP] IGG has finished. Starting FineTurbo.")
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
        beta, cp, omega = calc_xmf(self.xmf_param)
        print("Omega: " + str(omega))

        # clear events
        self.igg_event.clear()
        self.res_event.clear()
        print("igg event set: " + str(self.igg_event.is_set()))
        print("res event set: " + str(self.res_event.is_set()))
        try:
            foo = omega[-1]
        except IndexError as e:
            print(e)
            foo = 0
        return foo

        # return sum(individual) / sum([float(i[0]) for i in self.dp_genes]),

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
        self.optifig_xmf.clear()

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

        except (paramiko.ssh_exception.NoValidConnectionsError) as e:
            self.outputbox(e)

    def mutRestricted(self, individual, indpb):
        """
        Custom Mutation rule for keeping the genes in range.
        """
        if random.random() < indpb:
            for i, gene in enumerate(self.dp_genes):
                individual[i] = random.uniform(float(gene[0]), float(gene[1]))
        return individual,

    def populate(self):
        pop = self.toolbox.population(n=self.dp_POP_SIZE)
        # evaluate population
        fitnesses = list(map(self.toolbox.evaluate, pop))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit

        # extract fitnesses
        fits = [ind.fitness.values[0] for ind in pop]

        # number of generations
        g = 0
        # minlist = []

        while min(fits) > 0 and g < 1000:
            # new generation
            g += 1
            print("-- Generation %i --" % g)

            # select next generation individuals
            offspring = self.toolbox.select(pop, len(pop))
            # clone selected individual
            offspring = list(map(self.toolbox.clone, offspring))

            # crossover and mutations
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.dp_CXPB:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < self.dp_MUTPB:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            # evaluate individuals with invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            # replace entire existing population with offspring
            pop[:] = offspring

            # Gather all the fitnesses in one list and print the stats
            fits = [ind.fitness.values[0] for ind in pop]

            length = len(pop)
            mean = sum(fits) / length
            sum2 = sum(x * x for x in fits)
            std = abs(sum2 / length - mean ** 2) ** 0.5

            print("  Min %s" % min(fits))
            print("  Max %s" % max(fits))
            print("  Avg %s" % mean)
            print("  Std %s" % std)
            # minlist.append(min(fits))

        print("-- End of (successful) evolution --")

        best_ind = tools.selBest(pop, 1)[0]
        print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))

        # plt.plot(minlist)
        # plt.show()
        # pass
