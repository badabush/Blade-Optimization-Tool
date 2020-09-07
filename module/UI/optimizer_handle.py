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
            stdout = self.sshobj.send_cmd('export DISPLAY="localhost:16.0"')
            self.outputbox(stdout)
            stdout = self.sshobj.send_cmd("echo $DISPLAY")
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
        # get display address
        self.display = "export DISPLAY=" + self.box_DISPLAY.text() + ";"
        # project path
        projectpath = self.box_pathtodir.text()
        self.generate_script(projectpath)
        if projectpath[0] == "/" and projectpath[1] == "/":
            projectpath = projectpath[1:]
        projectpath = Path(projectpath)
        projectpath = projectpath.parts
        usr_folder = projectpath[-2]
        proj_folder = projectpath[-1]

        # run fine131 with script
        if not hasattr(self, 'sshobj'):
            self.ssh_connect()
        if self.sshobj.transport.is_active() == False:
            self.outputbox("Could not find active session.")
            return
        try:
            self.outputbox("opening FineTurbo..")
            stdout = self.sshobj.send_cmd(self.display + "/opt/numeca/bin/fine131 -script " + "/home/HLR/" + usr_folder + "/" +
                                          proj_folder + "/py_script/" + self.scriptname + " -batch -print")
            self.outputbox(stdout)
        except (jumpssh.exception.RunCmdError, jumpssh.exception.ConnectionError) as e:
            self.outputbox(e)

    def generate_script(self, dirpath):
        """
        Generate the script for running fine turbo.
        """
        self.scriptname = "script_run.py"
        file = open(dirpath + "/py_script/" + self.scriptname, "w")
        iec_name = "parent_V3/parent_V3.iec"
        # clean path for usage on the cluster
        if dirpath[0] == "/" and dirpath[1] == "/":
            dirpath = dirpath[1:]
        dirpath = Path(dirpath)
        dirpath = dirpath.parts
        usr_folder = dirpath[-2]
        proj_folder = dirpath[-1]
        self.scriptpath = "/home/HLR/" + usr_folder + "/" + proj_folder + "/py_script/"
        self.unixprojpath = "/home/HLR/" + usr_folder + "/" + proj_folder
        task_idx = str(0)
        no_iter = str(500)
        file.write('script_version(2.2)\n' +
                   'FT.open_project("/home/HLR/' + usr_folder + '/' + proj_folder + '/' + iec_name + '")\n' +
                   'FT.set_active_computations([1])\n' +
                   'FT.link_mesh_file("/home/HLR/' + usr_folder + '/' + proj_folder + '/Erstes_Netz_Tandem.igg",0)\n' +
                   'FT.set_nb_iter_max(' + no_iter + ')\n' +
                   'FT.task(' + task_idx + ').remove()\n' +
                   'FT.new_task()\n' +
                   'FT.task(' + task_idx + ').new_subtask()\n' +
                   'FT.task(' + task_idx + ').subtask(0).set_run_file("/home/HLR/' + usr_folder + '/' + proj_folder + '/parent_V3/parent_V3_brustinzidenz/parent_V3_brustinzidenz.run")\n' +
                   # 'FT.task(' + task_idx + ').start()\n' +
                   'FT.task(' + task_idx + ').subtask(0).set_compiler(3)\n' +
                   'FT.task(' + task_idx + ').start()'
                   )
        file.close()
        self.outputbox(
            "Writing script file to /home/HLR/" + usr_folder + "/" + proj_folder + "/py_script/" + self.scriptname)
        # open_igg_project("/home/HLR/liang/Tandem_Opti/Erstes_Netz_Tandem.igg")
        # save_project("/home/HLR/liang/Tandem_Opti/Erstes_Netz_Tandem.igg")
        # FT.link_mesh_file("/home/HLR/liang/Tandem_Opti/Erstes_Netz_Tandem.igg", 0)
        # FT.task(0).start()
        # FT.task(0).subtask(0).set_condition(0)
        # FT.task(0).start()
        # FT.task(0).subtask(0).set_condition(1)
        # FT.save_selected_computations()
