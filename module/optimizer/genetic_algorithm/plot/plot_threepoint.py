from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm as cm

def three_point(ds, ref_blade, logdir):
    fig, ax = plt.subplots(figsize=(10, 8), sharex='col', sharey='row')
    ref_omega = [ref_blade['omega_lower'], ref_blade['omega'], ref_blade['omega_upper']]
    ref_beta = np.rad2deg([ref_blade['beta_lower'], ref_blade['beta'], ref_blade['beta_upper']])
    best_omega = [ds.iloc[-1]['omega_lower'],ds.iloc[-1]['omega'],ds.iloc[-1]['omega_upper']]
    best_beta = [ds.iloc[-1]['beta_lower'], ds.iloc[-1]['beta'], ds.iloc[-1]['beta_upper']]

    ref_model = np.polyfit(ref_beta, ref_omega, 2)
    ref_model_fn = np.poly1d(ref_model)
    ref_dist = max([abs(ref_beta[0]-ref_beta[1]), abs(ref_beta[0]-ref_beta[1])])
    ref_x_s = np.linspace(ref_beta[0]-ref_dist, ref_beta[0]+ref_dist, 30)
    ax.plot(ref_x_s, ref_model_fn(ref_x_s), label="ref blade")
    
    best_model = np.polyfit(best_beta, best_omega, 2)
    best_model_fn = np.poly1d(best_model)
    best_dist = max([abs(best_beta[0]-best_beta[1]), abs(best_beta[0]-best_beta[1])])
    best_x_s = np.linspace(best_beta[0]-best_dist, best_beta[0]+best_dist, 30)
    ax.plot(best_x_s, best_model_fn(best_x_s), label="best blade")
    ax.legend()
    ax.set_xlabel("Beta")
    ax.set_ylabel("Omega")

    
    fig.savefig(Path(logdir + "/ref_best_three_point.png"))