from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt

from blade.bladegen import BladeGen
from blade.bladetools import get_blade_from_csv


def distributions(best_blades, logdir):
    """
    Generate plots for thickness and camber distributions. Pack camber and thickness data into lists with
    ref1/ref2/best1/best2 entries, save plots to log directory.

    :param best_blades: Blade parameters best blades
    :type best_blades: list
    :param logdir: path to log directory
    :type logdir: string
    :return:
    """

    ds_blades = []  # store blade parameters of ref1/ref2/best1/best2
    ds_thickness = []  # store thickness points of ref1/ref2/best1/best2
    ds_camber = []  # store camber points of ref1/ref2/best1/best2

    # get ref_blade parameters
    # _, ref1, ref2 = get_blade_from_csv(Path.cwd() / "UI/config/default_blade.csv")
    _, ref1, ref2 = get_blade_from_csv(Path.cwd() / "UI/config/default_blade2.csv")

    # assign best blade parameters
    ds_blades.append(ref1)
    ds_blades.append(ref2)
    ds_blades.append(best_blades[0])
    ds_blades.append(best_blades[1])

    # generate thickness and camber from BladeGen for all blades ref1/ref2/best1/best2
    for ds in ds_blades:
        bladegen = BladeGen(frontend="ui", nblade='single', th_dist_option=1, th=ds["th"], alpha1=ds["alpha1"],
                            alpha2=ds["alpha2"], x_maxcamber=ds["xmax_camber"], gamma_te=ds["gamma_te"],
                            x_maxth=ds["xmax_th"], l_chord=ds["l_chord"], lambd=ds["lambd"], th_le=ds["th_le"],
                            th_te=ds["th_te"], npts=1000)

        ds_thickness.append(bladegen.xy_th)
        ds_camber.append(bladegen.xy_camber)

    thickness_dist(ds_thickness, logdir)
    camber_dist(ds_camber, logdir)


def camber_dist(ds, dir):
    """
    Generate camber distribution subplot for front/aft blade.

    :param ds: camber data (ref1/ref2/best1/best2)
    :type ds: list
    :param dir: log directory
    :type dir: string
    :return:
    """

    fig, ax = plt.subplots(1, 2, sharey=True, figsize=(12, 6))
    fig.suptitle("Camber Distribution")
    ax_i = 0
    for i, camber in enumerate(ds):
        camber[:, 1] = np.arctan(np.gradient(camber[:, 1]) / np.gradient(camber[:, 0]))
        arc = camber[:, 1] + np.abs(np.min(camber[:, 1]))
        arc = arc * -1
        arc = arc + np.abs(np.min(arc))
        arc = arc / np.max(arc)
        xy = np.array([camber[:, 0], arc]).T

        # normalize so curves start at 0,0 and end at 1,1
        xy[:, 0] = xy[:, 0] / np.max(xy[:, 0])
        xy[:, 1] = xy[:, 1] / np.max(xy[:, 1])
        if i > 1:
            ax_i = 1
        ax[ax_i].plot(xy[:, 0], xy[:, 1], linewidth=2, alpha=.75)

    ax[0].plot([0, 1], [0, 1], "k--", linewidth=1, alpha=.5)
    ax[0].legend(["ref", "best"])
    ax[0].title.set_text("Front Blade")
    ax[0].grid()
    ax[0].set_xlim([0, 1])
    ax[0].set_ylim([0, 1])
    ax[0].set_xlabel("rel. chord")
    ax[0].axis("equal")

    ax[1].plot([0, 1], [0, 1], "k--", linewidth=1, alpha=.5)
    ax[1].legend(["ref", "best"])
    ax[1].title.set_text("Aft Blade")
    ax[1].grid()
    ax[1].set_xlim([0, 1])
    ax[1].set_ylim([0, 1])
    ax[1].set_xlabel("rel. chord")
    ax[1].axis("equal")

    fig.tight_layout()

    fig.savefig(Path(dir + "/camber_distribution.png"))


def thickness_dist(ds, dir):
    """
    Generate thickness distribution subplot for front/aft blade.

    :param ds: thickness data (ref1/ref2/best1/best2)
    :type ds: list
    :param dir: log directory
    :type dir: string
    :return:
    """

    fig, ax = plt.subplots(1, 2, sharey=True, figsize=(12, 6))
    fig.suptitle("Thickness Distribution")
    ax[0].plot(ds[0][:, 0], ds[0][:, 1] / np.max(ds[0][:, 1]), linewidth=2, alpha=.75)
    ax[0].plot(ds[2][:, 0], ds[2][:, 1] / np.max(ds[2][:, 1]), linewidth=2, alpha=.75)
    ax[0].legend(["ref", "best"])
    ax[0].title.set_text("Front Blade")
    ax[0].grid()
    ax[0].set_xlim([0, 1])
    ax[0].set_ylim([0, 1])
    ax[0].set_xlabel("rel. chord")
    ax[0].axis("equal")

    ax[1].plot(ds[1][:, 0], ds[1][:, 1] / np.max(ds[1][:, 1]), linewidth=2, alpha=.75)
    ax[1].plot(ds[3][:, 0], ds[3][:, 1] / np.max(ds[3][:, 1]), linewidth=2, alpha=.75)
    ax[1].legend(["ref", "best"])
    ax[1].title.set_text("Aft Blade")
    ax[1].grid()
    ax[1].set_xlim([0, 1])
    ax[1].set_ylim([0, 1])
    ax[1].set_xlabel("rel. chord")
    ax[1].axis("equal")

    fig.tight_layout()

    fig.savefig(Path(dir + "/thickness_distribution.png"))
