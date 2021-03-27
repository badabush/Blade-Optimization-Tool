import os
from pathlib import Path

from matplotlib import pyplot as plt

from UI.blade.blade_plots import bladePlot
from blade.bladetools import get_blade_from_csv

def deap_blade(blades, logdir):
    """
    DEAP Visualization Plot for blade shapes (reference blade/best blade from GA). Saves figure as blades.png in log
    directory logdir.

    :param blades: list of blades
    :type blades: list
    :param logdir: path of processed log where figure should be saved to
    :type logdir: string

    :return:
    """
    default_blade_path = Path(os.getcwd() + "/UI/config/default_blade.csv")
    default_blade = get_blade_from_csv(default_blade_path)
    # plot blades
    fig, ax = plt.subplots(figsize=(10, 8))
    # plot best blade

    bladePlot(ax, blades[0], ds1=blades[0], ds2=blades[1], alpha=.5)

    bladePlot(ax, default_blade[0], ds1=default_blade[1], ds2=default_blade[2], alpha=1, clear=False,
              transparent=True)
    ax.legend(["filled - best", "outline - reference"])
    fig.savefig(Path(logdir + "/blades.png"))