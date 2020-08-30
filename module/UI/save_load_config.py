from PyQt5.QtWidgets import QSizePolicy, QFileDialog
import numpy as np

from module.blade.bladetools import ImportExport, normalize
from module.UI.bladedesigner_handle import BDUpdateHandler
from pathlib import Path
import os
import csv

class SaveLoadConfig:

    def save_config(self):
        path = Path(os.getcwd() + "../../geo_output/blade_config")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()",
                                                  str(path) + "/savestate1.csv", "CSV Files (*.csv)", options=options)

        try:
            with open(fileName,'w') as csvfile:
                fields = list(self.ds.keys())
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                writer.writeheader()
                writer.writerow(self.ds)
                writer.writerow(self.ds1)
                writer.writerow(self.ds2)

        except IOError:
            print("I/O error")
        pass

    def load_config(self):
        path = Path(os.getcwd() + "../../geo_output/blade_config/")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", str(path),
                                                  "CSV Files (*.csv)", options=options)

        try:
            with open(fileName, 'r') as data:
                reader = csv.DictReader(data)
                ds_list = []
                for row in reader:
                    # values to float
                    for key in row.keys():
                        try:
                            if key == "pts":
                                pts = []
                                string = row[key]
                                string = string.strip("[").strip("]").split("]\n [")
                                for line in string:
                                    line = line.split(' ')
                                    slice = list(filter(None, line))
                                    slice = [float(i) for i in slice]
                                    pts.append(slice)
                                row[key] = np.array(pts)
                            else:
                                row[key] = float(row[key])
                        except ValueError:
                            pass
                    ds_list.append(row)
                # translate OrderedDict to dict
                self.ds = dict(ds_list[0])
                self.ds1 = dict(ds_list[1])
                self.ds2 = dict(ds_list[2])
        except IOError:
            print("I/O error")

        # update blade
        if self.nblades == 'single':
            self.set_labelval(self.ds)

        if self.nblades == 'tandem':
            self.radio_blade1.setChecked(True)
            self.set_labelval(self.ds1)
            self.radio_blade1.setChecked(False)
            self.radio_blade2.setChecked(True)
            self.set_labelval(self.ds2)
            # self.select_blade = 1
