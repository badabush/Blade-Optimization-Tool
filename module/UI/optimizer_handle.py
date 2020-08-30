from module.optimizer.ssh_login import ssh_connect
from module.optimizer.optimtools import read_top_usage
from module.UI.pandasviewer import pandasModel
from PyQt5.QtWidgets import QTableView


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
        self.btn_quota.clicked.connect(self.cmd_quota)


    def ssh_connect(self):
        """
        Connect with user data via ssh to the selected node.
        """
        self.sshobj = ssh_connect.Ssh_Util()
        if self.sshobj.failure:
            self.outputbox("No config.ini file found. Setup credentials first!")
            return
        self.outputbox("Connecting...")
        rcode = self.sshobj.ssh_connect()
        if rcode:
            self.outputbox("Error while connecting.")
        else:
            self.outputbox("Established Connection successfully.")


    def display_top(self):
        """
        Pass the command top (with some extras) and display a snap of stdout in a TableView Widget.
        """

        # check for existing connection
        if not hasattr(self, 'sshobj'):
            self.ssh_connect()

        try:
            self.outputbox("Passing Command.")
            stdout = self.sshobj.send_cmd("top -b -n 1")
            if not stdout is None:
                top_usage = read_top_usage(stdout)
                self.outputbox("Opening Widget.")
                self.pdwindow = pandasModel(top_usage)
                self.view = QTableView()
                self.view.setModel(self.pdwindow)
                self.view.resize(800, 600)
                self.view.show()

        except ValueError:
            self.outputbox("Error displaying pdTable.")


    def cmd_quota(self):
        """
        Send command quota, displays stdout.
        """
        # check for existing connection
        if not hasattr(self, 'sshobj'):
            self.ssh_connect()

        try:
            self.outputbox("Passing Command.")
            stdout = self.sshobj.send_cmd("quota")
            self.outputbox(stdout)
        except AttributeError:
            self.outputbox("Connecting...")