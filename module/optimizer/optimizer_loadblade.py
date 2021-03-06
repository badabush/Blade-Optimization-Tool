import pandas as pd
import numpy as np
import os
from pathlib import Path

from blade.bladegen import BladeGen
from optimizer.geomturbo import GeomTurboFile


class LoadBlade:
    def create_geomturbo(self, fname, path):
        blade = []
        # generate blades from parameter
        ds = self.ds
        z = np.zeros(int(ds['npts'] / 2))
        if ds['nblades'] == 'single':
            bladegen = BladeGen(frontend='UI', blade_df=ds)
            print('save single blade')
            blade_data, _ = bladegen._return()
            blade_flip = np.zeros(blade_data.shape)
            blade_flip[:, 0] = blade_data[:, 1]
            blade_flip[:, 1] = blade_data[:, 0]
            blade.append(np.array([z, blade_flip[:, 0], blade_flip[:, 1]]).T)
        else:
            for i in range(2):
                if (i == 0):
                    ds = self.ds1
                else:
                    ds = self.ds2
                bladegen = BladeGen(frontend='UI', blade_df=ds)
                blade_data, _ = bladegen._return()
                # blade = pd.DataFrame({'x': blade_data[:, 0], 'y': blade_data[:, 1]})
                # flip blade
                blade_flip = np.zeros(blade_data.shape)
                blade_flip[:, 0] = blade_data[:, 1]
                blade_flip[:, 1] = blade_data[:, 0]
                blade.append(np.array([z, blade_flip[:, 0], blade_flip[:, 1]]).T)

        rh = 0.5 * 0.172
        r = 0.043 * 0.01 + rh
        c_t = 0.043
        sc_t = 1.16
        s_t = sc_t + c_t
        l = 0.12
        N_t = np.round((2 * np.pi * rh) / s_t, 2)
        spacing = [self.ds2['x_offset'], self.ds2['y_offset']]
        try:
            GeomTurboFile(fname, path, ds['nblades'], blade, r, l, 2 * np.pi * rh / N_t, spacing)
        except:
            print("error creating geomTurbo file.")

    def create_trb(self, fname, path):
        temp_path = Path(os.getcwd() + "/optimizer/template/")
        save_path = Path(path)
        try:
            # f = open(temp_path / "trb_template.trb", "r")
            # f = open(temp_path / "TandemGridMedium.trb", "r")
            f = open(temp_path / "tandem_22_01_2021.trb", "r")
            # f = open(temp_path / "Template_Tandem_grob.trb", "r")
            fsave = open(save_path / (fname + ".trb"), "w")
            fsave.write(f.read())
        except FileNotFoundError:
            print("TRB template file not found.")
