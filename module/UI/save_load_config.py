from pathlib import Path
import os
import csv

from PyQt5.QtWidgets import QFileDialog

from module.blade.bladetools import get_blade_from_csv

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

    def load_config(self, fileName=""):
        if (fileName == "") or (fileName==False):
            path = Path(os.getcwd() + "../../geo_output/blade_config/")
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", str(path),
                                                      "CSV Files (*.csv)", options=options)

        try:
            self.ds, self.ds1, self.ds2 = get_blade_from_csv(fileName)
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
