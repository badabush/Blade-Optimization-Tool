from pathlib import Path

from matplotlib import pyplot as plt
import pandas as pd

def scatter_matrix(ds, logdir):
    # scatter matrix
    pd.plotting.scatter_matrix(ds, alpha=.2, figsize=(10, 8))
    plt.savefig(Path(logdir + "/scatter_matrix.png"))