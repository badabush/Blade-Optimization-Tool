import pandas as pd

from module.optimizer.ssh_login import ssh_connect
from module.optimizer.optimtools import read_top_usage
from module.UI.pandasviewer import pandasModel
from PyQt5.QtWidgets import QTableView
from PyQt5 import QtCore


class OptimHandler:
    """
    Contains update GUI elements for the Optimizer Tab.
    """

    def optim_handler_init(self):
        """
        Initialize optimizer tab gui elements e.g. link buttons
        """
        self.btn_testconnect.clicked.connect(self.ssh_connect)
        self.btn_topcmd.clicked.connect(self.display_top)


    def ssh_connect(self):
        self.sshobj = ssh_connect.Ssh_Util()
        if self.sshobj.failure:
            self.outputbox("No config.ini file found. Setup credentials first!")
            return
        rcode = self.sshobj.ssh_connect()
        if rcode:
            self.outputbox("Error while connecting.")
        else:
            self.outputbox("Established Connection successfully.")

    def display_top(self):

        if not hasattr(self, 'sshobj'):
            self.ssh_connect()
        try:
            self.outputbox("Connecting...")
            stdout = self.sshobj.send_cmd("top -b -n 1")
            top_usage = read_top_usage(stdout)

            self.pdwindow = pandasModel(top_usage)
            self.view = QTableView()
            self.view.setModel(self.pdwindow)
            self.view.resize(800, 600)
            self.view.show()
        except ValueError:
            self.outputbox("Error displaying pdTable.")

