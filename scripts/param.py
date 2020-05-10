import numpy as np
import pandas as pd

from tools import sdr


class Param:
    """
    class to load pandas file containing all parameters.

    """

    def __init__(self):
        """
        Generate and define parameters, then create a pandas df.

        """

        self.ds = self.generate()

        # construct pandas frame from Dict
        self.df_params = pd.DataFrame.from_dict(self.ds)
        0

    def generate(self):
        """


        :return:

        """
        ds = {}  # empty dataset dict, later used to append into pandas df_params

        # Lieblein Diffusion Factor for front and rear blade
        ds['df1'] = [.39]
        ds['df2'] = [.4915]
        ds['pp'] = [.915]
        ds['gap'] = [.03]  # [%]

        # medium radius
        ds['rh'] = [.5 * .172]
        ds['rs'] = [.5 * .24]

        # division radius
        ds['sc_s'] = [.43]
        ds['sc_t'] = [1.16]

        # chord length, identical tandem
        ds['c_s'] = [.043]
        ds['c_t'] = [ds['c_s'][0] / 2]

        # first cut S1 slightly above hub (1%gap)
        ds['r'] = [ds['c_s'][0] * .01 + ds['rh'][0]]

        # compute division
        ds['s_s'] = [ds['sc_s'][0] * ds['c_s'][0]]
        ds['s_t'] = [ds['sc_t'][0] * ds['c_t'][0]]

        # resulting number of blades
        ds['N_s'] = [np.round((2 * np.pi * ds['rh'][0]) / ds['s_s'][0])]
        ds['N_t'] = [np.round((2 * np.pi * ds['rh'][0]) / ds['s_t'][0])]

        # max camber position
        ds['a_s'] = [.43]
        ds['a_t1'] = [.46]
        ds['a_t2'] = [.46]

        # flow coefficient Cv
        ds['phi'] = [.65]

        # canal height
        ds['h_canal'] = [ds['rs'][0] - ds['rh'][0]]
        ds['hc'] = [ds['h_canal'][0] / ds['c_s'][0]]

        # real division: division and solicity
        ds['s'] = [2 * np.pi * ds['r'][0] / ds['N_s'][0]]  # division
        ds['sigma_s'] = [ds['c_s'][0] / ds['s_s'][0]]  # solicity s
        ds['sigma_t'] = [ds['c_t'][0] / ds['s_t'][0]]  # solicity t

        # relative thickness (reverse engineered from tandem); same abs. thickness on single and tandem,
        # thus only depenent on c_t
        ds['th'] = [.1 * ds['c_t'][0]]

        # relative thickness (tandem II (2.85%)), only 1/2 because of radius
        ds['th_LE'] = [.006 * ds['c_t'][0]]  # thickness leading edge
        ds['th_TE'] = [.0135 * ds['c_t'][0]]  # thickness trailing edge

        # angle to trailing edge
        ds['gammahk_s'] = [.07]
        ds['gammahk_t1'] = [.14]
        ds['gammahk_t2'] = [.14]

        # max thickness position (homogeneous for all parts), 40% ~ NACA65 Series
        ds['xd'] = [.4]

        # relative thickness
        ds['rth_s'] = [ds['th'][0] / ds['c_s'][0]]
        ds['rth_t'] = [ds['th'][0] / ds['c_t'][0]]

        # relative thickness trailing edge
        ds['rLE_s'] = [ds['th_LE'][0] / ds['c_s'][0]]
        ds['rTE_s'] = [ds['th_TE'][0] / ds['c_s'][0]]
        ds['rLE_t'] = [ds['th_LE'][0] / ds['c_t'][0]]
        ds['rTE_t'] = [ds['th_TE'][0] / ds['c_t'][0]]

        return ds

if __name__ == "__main__":
    Param().generate()
