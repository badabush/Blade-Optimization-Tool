import threading

from PyQt5.QtWidgets import QSizePolicy, QFileDialog
from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore
from optimizer.ssh_login.ssh_connect import SshUtil
from os.path import expanduser


class MeshGenUI(QtWidgets.QDialog):

    def __init__(self, ):
        super(MeshGenUI, self).__init__()
        uic.loadUi('UI/qtdesigner/meshgenwindow.ui', self)
        self.close_state = 0  # 0=close button, 1=generate button
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.btn_generate.clicked.connect(self.generate)
        self.btn_cls.clicked.connect(self.close)
        self.btn_geomturbopath.clicked.connect(self.project_explorer_geomturbo)
        self.btn_iggpath.clicked.connect(self.project_explorer_igg)

        # set default paths
        self.input_geomturbopath.setText("//130.149.110.81/liang/Tandem_Opti/BOT/template/autogrid/test_template.geomTurbo")
        self.input_iggpath.setText("//130.149.110.81/liang/Tandem_Opti/BOT/template/autogrid/")
        self.input_iggname.setText("test_template.igg")

    def project_explorer_geomturbo(self):
        """
        Opens a File Explorer to select geomTurbo file.
        :return: None
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()",
                                                  self.input_geomturbopath.text(),
                                                  "geomTurbo Files (*.geomTurbo)", options=options)
        self.input_geomturbopath.setText(fileName)

    def project_explorer_igg(self):
        """
        Opens a File Explorer to select geomTurbo file.
        :return: None
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        input_dir = QFileDialog.getExistingDirectory(self, "Open a folder", self.input_geomturbopath.text())
        self.input_iggpath.setText(input_dir)

    def generate(self):
        self.close_state = 1
        self.geomturbopath = self.input_geomturbopath.text()
        self.iggfolder = self.input_iggpath.text()
        self.iggname = self.input_iggname.text()
        self.close_window()

    def close_window(self):
        """
        Close Window on button clicked.
        """
        self.close()
