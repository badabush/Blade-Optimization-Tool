from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt, tri
import matplotlib
from matplotlib.ticker import MaxNLocator
import pandas as pd


def contour(ds, logdir):
    # contour plot
    filtered = ds.sort_values(["omega"], ascending=True)
    df_unique = filtered.groupby("omega").first().reset_index()
    ds = df_unique
    ngridx = 1 * len(ds.fitness)
    ngridy = 1 * len(ds.fitness)
    # FIXME
    ngrid = len(ds.fitness)
    x = ds.alph21
    y = ds.alph22
    z = ds.fitness
    fig, (ax1) = plt.subplots(nrows=1, figsize=(10, 8))
    xi = np.linspace(min(ds.alph11) - 0.05, max(ds.alph11) + 0.05, ngridx)
    yi = np.linspace(min(ds.alph12) - 0.005, max(ds.alph12) + 0.05, ngridy)
    triang = tri.Triangulation(x, y)
    interpolator_1 = tri.LinearTriInterpolator(triang, z)  # der kubische läuft irgendwie nicht...mh
    # interpolator_1 = tri.CubicTriInterpolator(triang, z)
    Xi, Yi = np.meshgrid(xi, yi)
    zi = interpolator_1(Xi, Yi)
    cntr1 = ax1.contourf(xi, yi, zi, levels=14, cmap="RdBu_r")
    fig.colorbar(cntr1, ax=ax1)
    ax1.scatter(x, y, facecolors='w', alpha=0.5, edgecolors='k', s=50)
    ax1.set(xlim=(min(ds.alph11), max(ds.alph11)), ylim=(min(ds.alph12), max(ds.alph12)))
    plt.subplots_adjust(hspace=0.5)
    # plt.show()
    # FIXME
    ax1.set_xlabel('alpha 1 (1) [-]')
    ax1.set_ylabel('alpha 2 (2) [-]')
    ax1.set_title('omega')
    fig.savefig(Path(logdir + "/xmaxcamber_fitness_contour.png"))


def contour2(df, logdir):
    # contour plot
    filtered = df.sort_values(["omega"], ascending=True)
    df_unique = filtered.groupby("omega").first().reset_index()
    df = df_unique

    feature = [
        [df.alph11, df.alph12, "alpha11_alpha12"],
        [df.alph11, df.alph21, "alpha11_alpha21"],
        [df.alph11, df.alph22, "alpha11_alpha22"],
        [df.alph12, df.alph21, "alpha12_alpha21"],
        [df.alph12, df.alph22, "alpha12_alpha22"],
        [df.alph21, df.alph22, "alpha21_alpha22"]
    ]
    for ds in feature:
        x = ds[0].to_numpy()
        y = ds[1].to_numpy()
        z = [df.omega.to_numpy(), df.fitness.to_numpy()]

        fig = plt.figure(figsize=(18, 7))

        for i in range(2):
            ax = fig.add_subplot(121+i, projection='3d')

            surf = ax.plot_trisurf(x, y, z[i], cmap=matplotlib.cm.jet, linewidth=0)
            fig.colorbar(surf)
            ax.set_xlabel(ds[2][:7])
            ax.set_ylabel(ds[2][8:])
            ax.set(zticklabels=[])
            ax.set(zlabel=None)

            if i==0:
                ax.set_title("Omega")
            else:
                ax.set_title("Fitness")
            ax.xaxis.set_major_locator(MaxNLocator(5))
            ax.yaxis.set_major_locator(MaxNLocator(6))
            ax.zaxis.set_major_locator(MaxNLocator(5))

            ax.view_init(elev=-90, azim=90)
        fig.tight_layout()
        fig.savefig(Path(logdir + "/" + ds[2] + '_contour.png'))