from PyQt5.QtWidgets import QSizePolicy
from PyQt5 import QtWidgets, uic

from optimizer.ssh_login.ssh_connect import SshUtil


class SSHLoginUi(QtWidgets.QMainWindow):

    def __init__(self):
        super(SSHLoginUi, self).__init__()
        uic.loadUi('UI/qtdesigner/loginwindow.ui', self)
        # chronological tabbing order
        self.setTabOrder(self.input_usr, self.input_pwd)
        self.setTabOrder(self.input_pwd, self.input_node)
        self.setTabOrder(self.input_node, self.btn_create)
        self.setTabOrder(self.btn_create, self.btn_cls)
        self.btn_create.clicked.connect(self.create_config)
        self.btn_cls.clicked.connect(self.close_window)
        # Connect Buttons to updating plot.

    def create_config(self):
        """
        When Button Create is clicked, get uname, pw and node from popup and write them into config.
        """
        username = self.input_usr.text()
        password = self.input_pwd.text()
        node = self.input_node.currentText()
        if (not self.input_usr) or (not self.input_pwd):
            #TODO: add print to outputbox
            return

        SshUtil.generate_config(username, password, node)
        self.close()

    def close_window(self):
        """
        Close Window on button clicked.
        """
        self.close()
