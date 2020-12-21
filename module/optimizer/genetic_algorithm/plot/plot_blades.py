import os
from pathlib import Path

from matplotlib import pyplot as plt

from module.UI.blade.blade_plots import bladePlot
from module.blade.bladetools import get_blade_from_csv

def deap_blade(blades, logdir):
    default_blade_path = Path(os.getcwd() + "/UI/config/default_blade.csv")
    default_blade = get_blade_from_csv(default_blade_path)
    # plot blades
    fig, ax = plt.subplots(figsize=(10, 8))
    # plot best blade

    bladePlot(ax, blades[0], ds1=blades[0], ds2=blades[1], alpha=.5)

    bladePlot(ax, default_blade[0], ds1=default_blade[1], ds2=default_blade[0], alpha=1, clear=False,
              transparent=True)
    fig.savefig(Path(logdir + "/blades.png"))