from PyQt5.QtWidgets import QSizePolicy, QFileDialog
from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore
from module.optimizer.ssh_login.ssh_connect import SshUtil
from os.path import expanduser


class DeapConfigUi(QtWidgets.QDialog):

    def __init__(self, ):
        super(DeapConfigUi, self).__init__()
        uic.loadUi('UI/qtdesigner/deapwindow.ui', self)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.btn_apply.clicked.connect(self.apply_)
        self.btn_cls.clicked.connect(self.close_)
        # self.btn_geomturbopath.clicked.connect(self.project_explorer_geomturbo)
        # self.btn_iggpath.clicked.connect(self.project_explorer_igg)
        self.deap_config_cb = {"pp": self.cb_pp,
                               "ao": self.cb_ao,
                               "division": self.cb_division,
                               "alpha1": self.cb_alpha1,
                               "alpha2": self.cb_alpha2,
                               "lambda": self.cb_lambda,
                               "th": self.cb_th,
                               "xmaxth": self.cb_xmaxth,
                               "xmaxcmb": self.cb_xmaxcmb,
                               "leth": self.cb_leth,
                               "teth": self.cb_teth}
        self.cblist = {}


    def get_checkbox(self):
        for key, widget in self.deap_config_cb.items():
            if widget.isChecked() == True:
                self.cblist[key] = 1
            else:
                self.cblist[key] = 0

    def close_(self):
        self.close()

    def apply_(self):
        self.get_checkbox()
        self.close_()
