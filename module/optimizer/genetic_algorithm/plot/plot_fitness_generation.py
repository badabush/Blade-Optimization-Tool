from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm as cm


def fitness_generation(ds, logdir):
    """
    Plot fitness over generation. Saves figure as fitness_generation.png

    :param ds: dataset from log
    :type ds: pd.DataFrame
    :param logdir: path of output directory
    :type logdir: string
    :return:
    """
    ds = np.reshape(ds, (len(ds), len(ds[0])))
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(ds[:,1])
    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness")
    gens = np.arange(1,len(ds)+1)
    ax.set_xticks(gens-1)
    xticklabel = []
    for gen in gens:
        xticklabel.append("GEN: {0}, POP: {1}".format(gen, int(ds[gen-1, 0])))
    ax.set_xticklabels(xticklabel, rotation=45, ha="right")
    plt.tight_layout()
    fig.savefig(Path(logdir + "/fitness_generation.png"))


def fitness_generation_scatter(ds, fitgen, logdir):
    """
    Plot best fitness over generation and scatter of all fitness values.
    Saves figure as fitness_generation_scatter.png.

    :param ds: dataset from log
    :type ds: pd.DataFrame
    :param fitgen: dataset of best fitness and generations
    :type fitgen: np.array
    :param logdir: path of output directory
    :type logdir: string
    :return:
    """
    # first figure
    fig, ax = plt.subplots(figsize=(10, 10))
    # data = np.reshape(ds, (len(ds), len(ds[0])))
    ax.grid()
    ax.plot(fitgen[:, 0], fitgen[:, 1], c="indianred", linewidth=3, alpha=.5)
    ax.scatter(np.linspace(0, np.max(fitgen[:, 0]), ds.fitness.shape[0]), ds.fitness.tolist(), s=.5, alpha=1)
    ax.set_ylabel("Fitness")
    # ax.set_xlim([0, 25])
    ax.set_ylim(np.min(fitgen[:, 1]) * .999, 1)
    ax.set_title("Fitness/Generation")
    ax.set_xlabel("Generation")
    # ax.set_xticklabels([])
    plt.tight_layout()
    fig.savefig(Path(logdir + "/fitness_generation_scatter.png"))