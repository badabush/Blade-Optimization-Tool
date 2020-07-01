import math
from PyQt5.QtWidgets import QSizePolicy, QFileDialog
from module.blade.bladetools import ImportExport, normalize
from matplotlib import pyplot as plt

class FileExplorer:
    """
    A very quick and dirty approach... Alternatively, creating a custom DoubleSlider class would be way cleaner.
    TODO: fix this when bored.
    """
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            ie = ImportExport()
            blade = ie._import(fileName)
            self.imported_blade = normalize(blade)
            0