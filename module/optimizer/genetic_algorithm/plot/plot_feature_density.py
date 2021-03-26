from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm as cm
from scipy.stats import gaussian_kde


def feature_density(ds, logdir):
    """
    Plot features over density
    :param ds:
    :param logdir:
    :return:
    """
    n_features = ds.shape[1] - 11
    fig, ax = plt.subplots(n_features, n_features, figsize=(12, 9), sharex='col', sharey='row')
    for row in range(n_features):
        for col in range(n_features):
            if row == col:
                min_col = min(ds.iloc[:, col])
                max_col = max(ds.iloc[:, col])
                n, bins, rects = ax[row, col].hist(ds.iloc[:, col], density=True, ec='k')
                max_height = max([rect.get_height() for rect in rects])
                for r in rects:
                    r.set_height(r.get_height() / max_height * (max_col - min_col) + min_col)
                ax[row, col].set_ylim(min_col, max_col)
            else:
                x = ds.iloc[:, col]
                y = ds.iloc[:, row]
                # calc density
                xy = np.vstack([x, y])
                z = gaussian_kde(xy)(xy)

                # sort by density (plotted last)
                idx = z.argsort()
                x, y, z = x[idx], y[idx], z[idx]
                ax[row, col].scatter(x, y, c=z, cmap=cm.RdBu)
            if col == 0:
                # shorten name
                if ds.columns[row] == "xmaxcamber1":
                    ax[row, col].set_ylabel("xmaxc1")
                elif ds.columns[row] == "xmaxcamber2":
                    ax[row, col].set_ylabel("xmaxc2")
                else:
                    ax[row, col].set_ylabel(ds.columns[row])
            if row == n_features - 1:
                if ds.columns[col] == "xmaxcamber1":
                    ax[row, col].set_xlabel("xmaxc1")
                elif ds.columns[col] == "xmaxcamber2":
                    ax[row, col].set_xlabel("xmaxc2")
                else:
                    ax[row, col].set_xlabel(ds.columns[col])
    fig.tight_layout()
    fig.savefig(Path(logdir + "/gene_output_density.png"))
