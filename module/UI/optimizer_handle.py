from pathlib import Path

from module.optimizer.ssh_login import ssh_connect
from module.optimizer.optimtools import read_top_usage
from module.UI.pandasviewer import pandasModel
from PyQt5.QtWidgets import QTableView
from module.UI.file_explorer import FileExplorer

import jumpssh


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
        self.btn_close_connection.clicked.connect(self.close_connection)
        self.btn_projectpath.clicked.connect(self.openFileNameDialogNumeca)
        self.btn_run.clicked.connect(self.run_script)

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

    def close_connection(self):
        """
        Closes the active ssh session.
        """
        try:
            if hasattr(self, 'sshobj'):
                self.outputbox("Closing Session.")
                self.sshobj.remote_session.close()
                self.sshobj.gateway_session.close()
            else:
                self.outputbox("No active Session.")
        except jumpssh.exception.RunCmdError:
            self.outputbox("Error closing Session.")


    def run_script(self):
        """
        Open file explorer to set project path.
        """

        if self.box_pathtodir.text() == "":
            self.outputbox("Set Path to Project Directory first!")
            return 0

        projectpath = self.box_pathtodir.text()
        self.generate_script(projectpath)

        # run fine131 with script
        if not hasattr(self, 'sshobj'):
            self.ssh_connect()
        if self.sshobj.remote_session.is_active() == False:
            self.outputbox("Could not find active session.")
            return
        try:
            self.outputbox("opening FineTurbo..")
            stdout = self.sshobj.send_cmd("cd "+ self.scriptpath)
            stdout = self.sshobj.send_cmd("/opt/numeca/bin/fine131 -script " + self.scriptname + "-batch")
            self.outputbox(stdout)
        except (jumpssh.exception.RunCmdError,jumpssh.exception.ConnectionError) as e:
            self.outputbox(e)

    def generate_script(self, dirpath):
        """
        Generate the script for running fine turbo.
        """
        self.scriptname = "script_run.py"
        file = open(dirpath + "/py_script/"+self.scriptname, "w")
        igg_name = "Erstes_Netz_Tandem.igg"
        # clean path for usage on the cluster
        if dirpath[0] == "/" and dirpath[1] == "/":
            dirpath = dirpath[1:]
        dirpath = Path(dirpath)
        dirpath = dirpath.parts
        usr_folder = dirpath[-2]
        proj_folder = dirpath[-1]
        self.scriptpath = "/home/HLR/" + usr_folder + "/" + proj_folder + "/py_script/"
        self.unixprojpath = "/home/HLR/" + usr_folder + "/" + proj_folder
        file.write("open_igg_project(" + self.scriptpath + igg_name + ")")
        file.close()
        self.outputbox("Writing script file to /home/HLR/" + usr_folder + "/" + proj_folder + "/py_script/"+self.scriptname)
        # open_igg_project("/home/HLR/liang/Tandem_Opti/Erstes_Netz_Tandem.igg")
        # save_project("/home/HLR/liang/Tandem_Opti/Erstes_Netz_Tandem.igg")
        # FT.link_mesh_file("/home/HLR/liang/Tandem_Opti/Erstes_Netz_Tandem.igg", 0)
        # FT.task(0).start()
        # FT.task(0).subtask(0).set_condition(0)
        # FT.task(0).start()
        # FT.task(0).subtask(0).set_condition(1)
        # FT.save_selected_computations()
