from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm as cm


def three_point(ds, ref_blade, logdir):
    """
    Plot 3 point curve of reference and fitness blade.
    Saves figure as ref_best_three_point.png .

    :param ds: dataset from log
    :type ds: pd.DataFrame
    :param ref_blade: reference blade parameters
    :type ref_blade: dict
    :param logdir: path of output directory
    :type logdir: string
    :return:
    """
    fig, ax = plt.subplots(figsize=(10, 8), sharex='col', sharey='row')
    ref_omega = [ref_blade['omega_lower'], ref_blade['omega'], ref_blade['omega_upper']]
    ref_beta = [ref_blade['beta_lower'], ref_blade['beta'], ref_blade['beta_upper']]
    best_omega = [ds.iloc[-1]['omega_lower'], ds.iloc[-1]['omega'], ds.iloc[-1]['omega_upper']]
    best_beta = ref_beta

    ref_model = np.polyfit(ref_beta, ref_omega, 2)
    ref_model_fn = np.poly1d(ref_model)
    # ref_dist = max([abs(ref_beta[0] - ref_beta[1]), abs(ref_beta[0] - ref_beta[1])])
    ref_x_s = np.linspace(ref_beta[0]-2, ref_beta[2]+2, 30)
    ax.plot(ref_x_s, ref_model_fn(ref_x_s), color="royalblue", label="ref blade")
    ax.scatter(ref_beta, ref_omega, marker='o', color="royalblue")

    if not (np.any(np.isnan(best_omega)) == True):
        best_model = np.polyfit(best_beta, best_omega, 2)
        best_model_fn = np.poly1d(best_model)
        # best_dist = max([abs(best_beta[0] - best_beta[1]), abs(best_beta[0] - best_beta[1])])
        best_x_s = np.linspace(ref_beta[0]-2, ref_beta[2]+2, 30)
        ax.plot(best_x_s, best_model_fn(best_x_s), label="best blade", color="indianred")
        ax.scatter(best_beta, best_omega, marker='o', color="indianred")

    ax.legend()
    ax.set_xlabel("Beta")
    ax.set_ylabel("Omega")

    fig.savefig(Path(logdir + "/ref_best_three_point.png"))
