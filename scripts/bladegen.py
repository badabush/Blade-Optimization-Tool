import pandas as pd
import numpy as np
from param import Param
import tools


class BladeGen:

    def __init__(self):
        self.df_param = Param().df_params
        self.beta = self.redir_tandem()
        self.lambd, self.theta = tools.naca65gen(self.beta['beta11'], self.beta['beta12'], self.df_param['sigma_t'],
                                                 self.df_param['rth_t'])
        0

    def redir_tandem(self):
        # ALL VALUES HAVE BEEN CHANGED TO RAD
        ds = self.df_param
        beta11 = np.deg2rad(53)
        beta12 = tools.sdr(beta11, ds['sigma_t'][0], ds['df1'][0])
        beta21 = beta12
        beta22 = tools.sdr(beta21, ds['sigma_t'][0], ds['df2'][0])
        df_t = (1 - (np.cos(beta11) / np.cos(beta22))) \
               + (np.cos(beta11) * (np.tan(beta11) - np.tan(beta22)) / (2 * (ds['c_s'][0] / ds['s_t'][0])))

        # dehaller over area ratio
        dehaller = np.cos(beta11) / np.cos(beta22)
        dehaller_fv = np.cos(beta11) / np.cos(beta12)
        dehaller_av = np.cos(beta12) / np.cos(beta22)

        # gather betas in a list
        beta = {'beta11': beta11,
                'beta12': beta12[0],
                'beta21': beta21[0],
                'beta22': beta22[0]}

        return beta


if __name__ == "__main__":
    BladeGen()
