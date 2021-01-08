from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm as cm
from scipy.stats import gaussian_kde

def feature_density(ds, logdir):
    fig, ax = plt.subplots(3, 2, figsize=(10, 8), sharex='col', sharey='row')
    for row in range(3):
        for col in range(2):
            x = ds.iloc[:, col]
            y = ds.iloc[:, row + 2]
            # calc density
            xy = np.vstack([x, y])
            z = gaussian_kde(xy)(xy)

            # sort by density (plotted last)
            idx = z.argsort()
            x, y, z = x[idx], y[idx], z[idx]
            ax[row, col].scatter(x, y, c=z, cmap=cm.RdBu)
            if col == 0:
                ax[row, col].set_ylabel(ds.columns[2 + row])
            if row == 2:
                ax[row, col].set_xlabel(ds.columns[col])
    fig.savefig(Path(logdir + "/gene_output_density.png"))