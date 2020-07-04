from PyQt5.QtWidgets import QSizePolicy, QFileDialog
import pandas as pd

from module.blade.bladetools import ImportExport, normalize
from module.blade.bladegen import BladeGen


class FileExplorer:
    """
    Class for Importing existing blade and exporting blade for the GUI.
    """

    def openFileNameDialog(self):
        """
        Opens a File Explorer to select .txt of blade for import.
        :return: None
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "../geo_output/matlab",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            ie = ImportExport()
            blade = ie._import(fileName)
            self.imported_blade = normalize(blade)
            self.update_in_control_vis(1)
            self.imported_blade_vis = 1

    def saveFileDialog(self):
        """
        Opens a File Explorer to select path for blade export.
        :return: None
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "../geo_output/py",
                                                  "Text Files (*.txt)", options=options)
        if fileName:
            ie = ImportExport()
            # generate blades from parameter
            ds = self.ds
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
                ds = pd.DataFrame({'x': blade_data[:, 0], 'y': blade_data[:, 1]})
                ie._export(fileName, ds)
            else:
                print("Only single blades are supported so far.")
