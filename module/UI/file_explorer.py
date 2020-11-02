from PyQt5.QtWidgets import QSizePolicy, QFileDialog
from PyQt5 import QtGui
import pandas as pd
from os.path import expanduser
from pathlib import Path

from module.blade.bladetools import ImportExport, normalize
from module.blade.bladegen import BladeGen


class FileExplorer:
    """
    Class for File dialog popups.
    """

    def project_explorer_dir(self):
        """
        Opens a File Explorer to select Project folder.
        :return: None
        """

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        input_dir = QFileDialog.getExistingDirectory(self, "Open a folder", expanduser("~"))
        self.box_pathtodir.setText(input_dir)

    def project_explorer_iec(self):
        """
        Opens a File Explorer to select iec file.
        :return: None
        """

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", self.box_pathtodir.text(),
                                                  "IEC Files (*.iec)", options=options)
        self.box_pathtoiec.setText(fileName)

    def project_explorer_igg(self):
        """
        Opens a File Explorer to select igg file.
        :return: None
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", self.box_pathtodir.text(),
                                                  "Mesh Files (*.igg)", options=options)
        self.box_pathtoigg.setText(fileName)

    def project_explorer_run(self):
        """
        Opens a File Explorer to select run file.
        :return: None
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", self.box_pathtodir.text(),
                                                  "RUN Files (*.run)", options=options)
        self.box_pathtorun.setText(fileName)

    def project_explorer_geomturbo(self):
        """
        Opens a File Explorer to select geomTurbo file.
        :return: None
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", self.box_pathtodir.text(),
                                                  "geomTurbo Files (*.geomTurbo)", options=options)
        self.box_pathtogeomturbo.setText(fileName)

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
            if self.nblades == 'single':
                blade = ie._import(fileName)
                self.imported_blade = normalize(blade)
            else:
                fname1 = Path(fileName).parts[-1]
                if '_FV' in fname1:
                    fname2 = fname1.replace('FV', 'AV')
                    blade1 = ie._import(fileName)
                    blade2 = ie._import(fileName.replace(fname1, fname2))
                elif '_AV' in fname1:
                    fname2 = fname1.replace('AV', 'FV')
                    blade2 = ie._import(fileName)
                    blade1 = ie._import(fileName.replace(fname1, fname2))
                self.imported_blade1 = normalize(blade1)/2
                self.imported_blade2 = normalize(blade2)/2
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
                head, _sep, tail = fileName.rpartition(".")
                if head == "":
                    head = tail
                for i in range(2):
                    if (i == 0):
                        ds = self.ds1

                        fname = head + "_FV.txt"
                    else:
                        ds = self.ds2
                        fname = head + "_AV.txt"
                    bladegen = BladeGen(frontend='UI', nblade=ds['nblades'], th_dist_option=ds['thdist_ver'],
                                        npts=ds['npts'],
                                        alpha1=ds['alpha1'], alpha2=ds['alpha2'],
                                        lambd=ds['lambd'], th=ds['th'], x_maxth=ds['xmax_th'],
                                        x_maxcamber=ds['xmax_camber'],
                                        l_chord=ds['l_chord'], th_le=ds['th_le'], th_te=ds['th_te'],
                                        spline_pts=ds['pts'],
                                        thdist_points=ds['pts_th'])
                    blade_data, _ = bladegen._return()
                    ds = pd.DataFrame({'x': blade_data[:, 0], 'y': blade_data[:, 1]})

                    ie._export(fname, ds)
