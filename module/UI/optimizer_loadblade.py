import pandas as pd
import numpy as np
from module.blade.bladegen import BladeGen
from module.optimizer.geomturbo import GeomTurboFile


class LoadBlade:
    def load_geomturbo(self):
        blade = []
        # generate blades from parameter
        ds = self.ds
        z = np.zeros(int(ds['npts']/2))
        if ds['nblades'] == 'single':
            bladegen = BladeGen(frontend='UI', nblade=ds['nblades'], th_dist_option=ds['thdist_ver'],
                                npts=ds['npts'],
                                alpha1=ds['alpha1'], alpha2=ds['alpha2'],
                                lambd=ds['lambd'], th=ds['th'], x_maxth=ds['xmax_th'],
                                x_maxcamber=ds['xmax_camber'],
                                l_chord=ds['l_chord'], th_le=ds['th_le'], th_te=ds['th_te'], spline_pts=ds['pts'],
                                thdist_points=ds['pts_th'])
            print('save single blade')
            blade_data, _ = bladegen._return()
            blade_flip = np.zeros(blade_data.shape)
            blade_flip[:,0] = blade_data[:,1]
            blade_flip[:,1] = blade_data[:,0]
            blade.append(np.array([z,blade_flip[:,0], blade_flip[:,1]]).T)
        else:
            for i in range(2):
                if (i == 0):
                    ds = self.ds1
                else:
                    ds = self.ds2
                bladegen = BladeGen(frontend='UI', nblade=ds['nblades'], th_dist_option=ds['thdist_ver'],
                                    npts=ds['npts'],
                                    alpha1=ds['alpha1'], alpha2=ds['alpha2'],
                                    lambd=ds['lambd'], th=ds['th'], x_maxth=ds['xmax_th'],
                                    x_maxcamber=ds['xmax_camber'],
                                    l_chord=ds['l_chord'], th_le=ds['th_le'], th_te=ds['th_te'], spline_pts=ds['pts'],
                                    thdist_points=ds['pts_th'])
                blade_data, _ = bladegen._return()
                # blade = pd.DataFrame({'x': blade_data[:, 0], 'y': blade_data[:, 1]})
                # flip blade
                blade_flip = np.zeros(blade_data.shape)
                blade_flip[:,0] = blade_data[:,1]
                blade_flip[:,1] = blade_data[:,0]
                blade.append(np.array([z, blade_flip[:, 0], blade_flip[:, 1]]).T)
        path = self.paths["dir_raw"] + '/BOT/geomturbo_files/'
        rh = 0.5 * 0.172
        r = 0.043 * 0.01 + rh
        c_t = 0.043
        sc_t = 1.16
        s_t = sc_t + c_t
        l = 0.12
        N_t = np.round((2 * np.pi * rh) / s_t, 2)

        GeomTurboFile(path, ds['nblades'], blade, r, l, 2 * np.pi * rh/N_t)
