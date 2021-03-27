from pathlib import Path

import matplotlib.pyplot as plt

def feature_time(ds, logdir):
    """
    Plot features (free parameters) over time. Saves figure as alph_time.png.

    :param ds: dataset from log
    :type ds: pd.DataFrame
    :param logdir: path of output directory
    :type logdir: string
    :return:
    """
    fig, ax = plt.subplots(4, 1, sharex=True, figsize=(10, 8))
    # FIXME
    ax[0].plot(ds.alph11, label="alpha 11")
    ax[0].legend()
    # ax[0].set_ylabel("Percent Pitch [-]")
    ax[0].set_ylabel("alpha1 (1) [-]")
    ax[1].plot(ds.alph12, label="alpha 12")
    ax[1].set_xlabel("Iteration")
    # ax[1].set_ylabel("Axial Overlap [-]")
    ax[1].set_ylabel("alpha2 (1) [-]")
    ax[2].plot(ds.alph21, label="alpha 21")
    ax[2].set_xlabel("Iteration")
    # ax[1].set_ylabel("Axial Overlap [-]")
    ax[2].set_ylabel("alpha1 (2) [-]")
    ax[3].plot(ds.alph22, label="alpha 22")
    ax[3].set_xlabel("Iteration")
    # ax[1].set_ylabel("Axial Overlap [-]")
    ax[3].set_ylabel("alpha2 (2) [-]")
    ax[1].legend()
    fig.savefig(Path(logdir + "/alph_time.png"))

