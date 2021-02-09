from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm as cm


def fitness_generation(ds, logdir):

    # first figure
    fig, ax = plt.subplots(figsize=(12, 4))
    data = np.reshape(ds[0], (len(ds[0]), len(ds[0][0])))
    ax.grid()
    ax.plot(data[:,1],linewidth=3)
    ax.set_ylabel("Fitness")
    ax.set_xlim([0, 25])
    ax.set_ylim([0.9034, 0.906])
    ax.set_title("Fitness/Generation")
    # ax.set_xlabel("Generation")
    ax.set_xticklabels([])
    plt.tight_layout()
    fig.savefig(Path(logdir + "/fitness_generation_cx07_mut03.png"))

    # second figure
    fig, ax = plt.subplots(figsize=(12, 4.3))
    data = np.reshape(ds[1], (len(ds[1]), len(ds[1][0])))
    ax.grid()
    ax.plot(data[:,1],linewidth=3)
    ax.set_ylabel("Fitness")
    ax.set_xlim([0, 25])
    ax.set_ylim([0.9034, 0.906])
    # ax.set_title("Fitness/Generation")
    ax.set_xlabel("Generation")
    plt.tight_layout()
    fig.savefig(Path(logdir + "/fitness_generation_cx08_mut02.png"))
    # ax.set_xticklabels([])

        # gens = np.arange(1,len(ds)+1)
        # ax.set_xticks(gens-1)
        # xticklabel = []
        # for gen in gens:
        #     xticklabel.append("{gen}".format(gen=gen))
        # ax.set_xticklabels(xticklabel, rotation=45, ha="right")


