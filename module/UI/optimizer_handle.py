from pathlib import Path
import jumpssh
import time
import threading
import os
import queue

from PyQt5.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.animation as animation
from pyface.qt import QtGui
from PyQt5.QtWidgets import QTableView

from module.optimizer.ssh_login import ssh_connect
from module.optimizer.optimtools import read_top_usage
from module.UI.pandasviewer import pandasModel
from module.optimizer.xml_parser import parse_res
from module.optimizer.generate_script import gen_script


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
        self.btn_kill.clicked.connect(self.kill_loop)
        self.box_terminal.moveCursor(QtGui.QTextCursor.End)

        # init plot
        self.optifig = OptimPlotCanvas(self, width=8, height=10)
        toolbar = NavigationToolbar(self.optifig, self)
        centralwidget = self.optimfig_widget
        vbl = QtGui.QVBoxLayout(centralwidget)
        vbl.addWidget(toolbar)
        vbl.addWidget(self.optifig)
        # self.setCentralWidget(self.graphWidget)

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
        self.scriptname = gen_script(projectpath)
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
            # sending command with display | fine version location | script + location | batch | print
            stdout = self.sshobj.send_cmd(
                self.display + "/opt/numeca/bin/fine131 -script " + "/home/HLR/" + usr_folder + "/" +
                proj_folder + "/py_script/" + self.scriptname + " -batch -print")
            self.outputbox(stdout)

            # start thread to read res file
            t = threading.Thread(name='res_reader', target=self.read_res)
            t.start()

        except (jumpssh.exception.RunCmdError, jumpssh.exception.ConnectionError) as e:
            self.outputbox(e)


    def read_res(self):
        """
        Waiting for FineTurbo to create the .res file, then read it periodically in one thread and plot it in another
        thread. New data is handled by queueing.
        """

        self.outputbox("starting thread for reading .res-file.")
        self.kill = False
        ds_res = {}
        res_file = "//130.149.110.81/liang/Tandem_Opti/parent_V3/parent_V3_brustinzidenz/parent_V3_brustinzidenz.res"
        # delete old .res file
        try:
            os.remove(res_file)
        except FileNotFoundError:
            pass
        timeout = 0
        # wait for fineTurbo to start calculation by checking for the existance of .res-file
        # timeout at 30s
        while timeout <= 30:
            if os.path.exists(res_file):
                break
            self.outputbox("Waiting for Process, timeout (" + str(timeout) + "/30)")
            timeout += 1
            time.sleep(1)
        #start thread for .res reader generator
        if (timeout == 30):
            return

        self.outputbox("Beginning computation ..")
        q = queue.Queue()
        t2 = threading.Thread(name='res_generator', target=parse_res, args=(res_file, q, self.kill))
        t2.start()

        while (self.kill == False):
            try:
                # get new data from queue
                val = q.get()
                idx = int(val[0])
                ds_res[idx] = val
                print(val)
                self.optifig.animate(ds_res)
                # self.outputbox("idx: " + str(self.idx))
            except TypeError as e:
                print(e)
            time.sleep(.1)

    def kill_loop(self):
        self.kill = True


class OptimPlotCanvas(FigureCanvas):
    """
    Real-Time plot of data from .res file.
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.ax = self.figure.add_subplot(111)
        self.ax.grid()
        self.xlim = (0, 0)
        self.ylim = (0, 0)
        ani = animation.FuncAnimation(fig, self.animate, interval=1000)

    def animate(self, ds):
        xs = []
        inlet = []
        outlet = []
        for key, val in ds.items():
            xs.append(int(key))
            inlet.append(float(val[8]))
            outlet.append(float(val[9]))

        # self.ax.clear()
        self.ax.plot(xs, inlet, color='royalblue')
        self.ax.plot(xs, outlet, color='indianred')
        self.draw()
