#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.


#    example which maximizes the sum of a list of integers
#    each of which can be 0 or 1

import random

import numpy as np
from matplotlib import pyplot as plt

from deap import base
from deap import creator
from deap import tools
from deap import benchmarks

# min / max, fixed(bool)
genes = np.array([
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
IND_SIZE = genes.shape[0]
POP_SIZE = 100
CXPB, MUTPB = .5, .2  # crossover probability, mutation probability


class TestGA:
    def __init__(self):
        """
            Parameters:
                * PP [0.85, 0.95]
                * AO [-0.1, 0.1]
            """

        # Creator
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        # Toolbox
        self.toolbox = base.Toolbox()

        # Attribute generator
        list(self.toolbox.register("attr_%s" % i[3], random.uniform, float(i[0]), float(i[1])) for i in genes)

        # self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_item, n=IND_SIZE)
        self.toolbox.register("individual", tools.initCycle, creator.Individual,
                              (self.toolbox.attr_pp, self.toolbox.attr_ao, self.toolbox.attr_div,
                               self.toolbox.attr_alph1, self.toolbox.attr_alph2, self.toolbox.attr_lambd,
                               self.toolbox.attr_th, self.toolbox.attr_xmaxth, self.toolbox.attr_xmaxch,
                               self.toolbox.attr_leth, self.toolbox.attr_teth), n=1)

        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        self.toolbox.register("evaluate", self.eval)
        # self.toolbox.register("evaluate", benchmarks.ackley)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", self.mutRestricted, indpb=.3)
        # self.toolbox.register("mutate", tools.mutFlipBit, indpb=.05)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

        self.populate()

    def eval(self, individual):
        # individuals will be fed to Fine, return omega to minimize

        return sum(individual) / sum([float(i[0]) for i in genes]),

    def mutRestricted(self, individual, indpb):
        if random.random() < indpb:
            for i, gene in enumerate(genes):
                individual[i] = random.uniform(float(gene[0]), float(gene[1]))
        return individual,
    

    def populate(self):
        pop = self.toolbox.population(n=POP_SIZE)
        # evaluate population
        fitnesses = list(map(self.toolbox.evaluate, pop))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit

        # extract fitnesses
        fits = [ind.fitness.values[0] for ind in pop]

        # number of generations
        g = 0
        minlist = []

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
                if random.random() < CXPB:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < MUTPB:
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
            minlist.append(min(fits))

        print("-- End of (successful) evolution --")

        best_ind = tools.selBest(pop, 1)[0]
        print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))

        plt.plot(minlist)
        plt.show()
        pass


if __name__ == "__main__":
    # random.seed(123)
    TestGA()
