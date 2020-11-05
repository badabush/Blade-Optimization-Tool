import paramiko
import time, datetime
import threading
import os, glob
import queue
from pathlib import Path
import numpy as np

from PyQt5.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from pyface.qt import QtGui
from PyQt5.QtWidgets import QTableView
import configparser

from module.optimizer.ssh_login import ssh_connect
from module.optimizer.optimtools import read_top_usage, parse_res, cleanpaths, read_xmf
from module.optimizer.generate_script import gen_script
from module.optimizer.pandasviewer import pandasModel
from module.UI.generate_mesh_ui import MeshGenUI


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
        self.btn_gen_mesh.clicked.connect(self.create_meshfile)
        self.btn_close_connection.clicked.connect(self.close_connection)
        self.btn_projectpath.clicked.connect(self.project_explorer_dir)
        self.btn_projectiec.clicked.connect(self.project_explorer_iec)
        self.btn_projectigg.clicked.connect(self.project_explorer_igg)
        self.btn_projectrun.clicked.connect(self.project_explorer_run)
        self.btn_projectgeomturbo.clicked.connect(self.project_explorer_geomturbo)
        self.btn_run.clicked.connect(self.run_script)
        self.btn_kill.clicked.connect(self.kill_loop)
        self.opt_btn_update_param.clicked.connect(self.update_param)

        # init LEDs
        self.toggle_leds(self.led_connection, 0)
        self.toggle_leds(self.led_mesh, 0)

        # init plot
        self.optifig_massflow = OptimPlotMassflow(self, width=8, height=10)
        toolbar = NavigationToolbar(self.optifig_massflow, self)
        centralwidget = self.optimfig_widget
        vbl = QtGui.QVBoxLayout(centralwidget)
        vbl.addWidget(toolbar)
        vbl.addWidget(self.optifig_massflow)

        self.optifig_xmf = OptimPlotXMF(self, width=8, height=10)
        toolbar = NavigationToolbar(self.optifig_xmf, self)
        centralwidget2 = self.optimfig_widget_2
        vbl = QtGui.QVBoxLayout(centralwidget2)
        vbl.addWidget(toolbar)
        vbl.addWidget(self.optifig_xmf)

        # set default paths for lazy development
        self.box_pathtodir.setText("//130.149.110.81/liang/Tandem_Opti")
        self.box_pathtoiec.setText("//130.149.110.81/liang/Tandem_Opti/parent_V3/parent_V3.iec")
        self.box_pathtoigg.setText("//130.149.110.81/liang/Tandem_Opti/BOT/template/autogrid/test_template.igg")
        self.box_pathtorun.setText(
            "//130.149.110.81/liang/Tandem_Opti/parent_V3/parent_V3_brustinzidenz/parent_V3_brustinzidenz.run")
        # self.box_pathtogeomturbo.setText("//130.149.110.81/liang/Tandem_Opti/BOT/geomturbo_files/testgeom.geomTurbo")

        # grab paths

        self.paths = {}
        self.grab_paths

        # init XMF dict
        self.xmf_param = {}  # [['Inlet', Outlet'], ...]
        self.xmf_param['abs_total_pressure'] = []
        self.xmf_param['static_pressure'] = []
        self.xmf_param['y_velocity'] = []
        self.xmf_param['z_velocity'] = []
        self.xmf_param['i'] = []

    def toggle_leds(self, led, state):
        if state == 0:
            pixmap = QtGui.QPixmap(os.getcwd() + "/UI/icons/red-led-on.png")
        else:
            pixmap = QtGui.QPixmap(os.getcwd() + "/UI/icons/green-led-on.png")
        pixmap2 = pixmap.scaled(20, 20)
        led.setPixmap(pixmap2)

    def grab_paths(self):
        self.paths['dir'] = self.box_pathtodir.text()
        self.paths['iec'] = self.box_pathtoiec.text()
        self.paths['run'] = self.box_pathtorun.text()
        self.paths['igg'] = self.box_pathtoigg.text()
        # try:
        # self.paths['geomturbo'] = self.meshgen.geomturbopath
        # except AttributeError as e:
        #     print(e)
        # self.paths['igg'] = ""
        # self.paths['geomturbo'] = ""
        self.paths = cleanpaths(self.paths)

    def ssh_connect(self):
        """
        Connect with user data via ssh to the selected node.
        """
        self.sshobj = ssh_connect.SshUtil()
        if self.sshobj.failure:
            self.outputbox("No config.ini file found. Setup credentials first!")
            return
        self.outputbox("Connecting...")
        rcode = self.sshobj.ssh_connect()
        if rcode:
            self.outputbox("Error while connecting.")
            self.toggle_leds(self.led_connection, 0)
        else:
            self.outputbox("Established Connection successfully.")
            self.toggle_leds(self.led_connection, 1)

    def update_param(self):
        """ Get parameters from Control. """
        self.opt_param["niter"] = int(self.opt_input_iteration.value())
        self.opt_param["cores"] = int(self.opt_input_cores.value())
        config = configparser.ConfigParser()
        config.read(os.getcwd() + '/optimizer/ssh_login/ssh_config.ini')
        self.opt_param["node"] = config['ssh']['node']
        self.opt_param["convergence"] = int(self.opt_input_convergence.value())

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
        except paramiko.ssh_exception.NoValidConnectionsError:
            self.outputbox("Error closing Session.")

    def run_script(self):
        """
        Open file explorer to set project path.
        """
        # update params from control
        self.update_param()
        # refresh paths
        self.grab_paths()
        # clear plot
        self.optifig_massflow.animate_massflow({})

        if self.box_pathtodir.text() == "":
            self.outputbox("Set Path to Project Directory first!")
            return 0
        # get display address
        self.display = "export DISPLAY=" + self.box_DISPLAY.text() + ";"

        # get node_id, number of cores, writing frequency here
        self.scriptfile = gen_script(self.paths, self.opt_param)

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
                self.display + "/opt/numeca/bin/fine131 -script " + "/home/HLR/" + self.paths['usr_folder'] + "/" +
                self.paths['proj_folder'] + "/BOT/py_script/" + self.scriptfile + " -batch -print")
            self.outputbox(stdout)

            # if self.first_run == True:
            # start thread to read res file
            t = threading.Thread(name='res_reader', target=self.read_res)
            t.start()

        except (paramiko.ssh_exception.NoValidConnectionsError) as e:
            self.outputbox(e)

    def read_res(self):
        """
        Waiting for FineTurbo to create the .res file, then read it periodically in one thread and plot it in another
        thread. New data is handled by queueing.
        General idea is emptying the queue in chunks, meaning every iteration, everything will be read from the queue to
        minimize workload on CPU.
        """

        self.outputbox("starting thread for reading .res-file.")

        self.pause_loop = False
        ds_res = {}
        ds_xmf = {}

        res_file = self.paths['res']
        xmf_file = self.paths['xmf']
        # delete old .res file
        try:
            os.remove(res_file)
        except (FileNotFoundError, PermissionError):
            print("No .res file removed.")
        timeout = 0
        # wait for fineTurbo to start calculation by checking for the existence of .res-file
        # timeout at 30s
        while timeout <= 300:
            if os.path.exists(res_file):
                break
            elif self.pause_loop:
                return
            if timeout % 10 == 0:
                self.outputbox("Waiting for Process, timeout (" + str(timeout) + "/300)")
            timeout += 1
            time.sleep(1)

        # start thread for .res reader generator
        if (timeout >= 300):
            self.outputbox("Error starting the process. Check FineTaskmanager window.")
            return

        self.outputbox("Starting computation ..")
        start_time = datetime.datetime.now()
        q_res = queue.Queue()
        # q_xmf = queue.Queue()
        self.event = threading.Event()
        t_res = threading.Thread(name='res_generator', target=parse_res, args=(res_file, q_res, self.event))
        t_res.start()

        # reset and clear queue and plot
        self.optifig_massflow.clear()
        self.optifig_xmf.clear()
        q_res.queue.clear()
        # q_xmf.queue.clear()
        idx = 0

        niter = self.opt_param["niter"]
        while not self.event.is_set():
            try:
                # get new data from queue
                if (self.pause_loop == True):
                    time.sleep(5)
                else:
                    # empty queue in chunks to minimize processor workload
                    while not q_res.empty():
                        val = q_res.get()
                        idx = int(val[0])
                        ds_res[idx] = val
                        # plot2 every 500 steps (writing frequency)
                        if (idx - 100) % 500 == 0:
                            self.xmf_param['i'].append(idx)
                            self.xmf_param = read_xmf(xmf_file, self.xmf_param)
                            self.optifig_xmf.animate_xmf(self.xmf_param)
                    self.optifig_massflow.animate_massflow(ds_res)

                    # TODO: implement another way of recognizing end of iterations e.g. timeout
                    if (idx == (niter + 100)):
                        self.outputbox("Cleaning up.")
                        time.sleep(5)
                        # set events, end taskmanager, end parseres, kill while loops
                        self.kill_loop()
                        # save values from XMF
                        self.xmf_param = read_xmf(xmf_file, self.xmf_param)

                        # display time elapsed
                        elapsed_time = datetime.datetime.now() - start_time
                        min, sec = divmod(elapsed_time.seconds, 60)
                        hour, min = divmod(min, 60)
                        self.outputbox("Total time elapsed: " + str(hour) + ":" + str(min) + ":" + str(sec))

            except TypeError as e:
                print(e)

            time.sleep(1)

    def create_meshfile(self):
        """
        Opens the Mesh Generation Window.
        """
        self.meshgen = MeshGenUI()
        # self.meshgen.show()
        self.meshgen.exec_()
        # check for existing connection
        if not hasattr(self, 'sshobj'):
            self.ssh_connect()
        try:
            t = threading.Thread(name="create_meshfile", target=self.run_igg)
            t.start()
        except AttributeError:
            self.outputbox("Connecting...")

    def run_igg(self):
        # get path from dialog window
        self.grab_paths()
        geomturbopath = self.meshgen.geomturbopath
        geomturboname = Path(geomturbopath).parts[-1].split('.')[0]
        path = self.meshgen.iggfolder
        iggname = self.meshgen.iggname.split('.')[0]
        unix_projpath = "/home/HLR/" + self.paths['usr_folder'] + '/' + self.paths['proj_folder']
        path_unix = path.replace(self.paths['dir_raw'], unix_projpath)
        gT_unix = geomturbopath.replace(self.paths['dir_raw'], unix_projpath)

        # delete existing files in /autogrid/
        try:
            files = glob.glob(path + '/*')
            for f in files:
                os.remove(f)
        except OSError:
            pass
        # create .geomTurbo and .trb in folder
        self.create_geomturbo(geomturboname, path)
        self.create_trb(iggname, path)
        self.display = "export DISPLAY=" + self.box_DISPLAY.text() + ";"
        self.outputbox("Generating Mesh. This might take a while.")
        stdout = self.sshobj.send_cmd(
            self.display + "/opt/numeca/bin/igg131 -batch -print -autogrid5 " +
            "-trb " + path_unix + iggname + ".trb " +
            " -geomTurbo " + gT_unix + " " +
            " -mesh " + path_unix + iggname + ".igg " +
            "-niversion 131"
        )
        if ("Writing Configuration File... Done" in stdout) and ("Exit IGG Background Session" in stdout):
            self.outputbox("Successfully created Meshfile in Autogrid.")
            self.toggle_leds(self.led_mesh, 1)
        else:
            self.outputbox("Error creating Meshfile with Autogrid.")

    def kill_loop(self):
        """
        Kills the loop and the process of the TaskManager.

        :raise: AttributeError
        """
        # self.kill = True
        self.pause_loop = True

        # case for event not set, e.g. kill is pressed before first run
        try:
            self.event.set()
        except AttributeError as e:
            print(e)
        if not hasattr(self, 'sshobj'):
            self.ssh_connect()
        try:
            self.outputbox("Attempting to kill process.")
            stdout = self.sshobj.send_cmd(
                'ps aux | grep -v grep | grep "/opt/numeca/fine131/LINUX/fine/taskManagerx86_64" | grep "[f]ine" | grep "' + self.box_DISPLAY.text() + '"' + " | awk '{print $2}'")
            if stdout == "":
                self.outputbox("No running processes found.")
                return
            else:
                stdout = self.sshobj.send_cmd("kill " + str(stdout))
                self.outputbox("Killed fine taskManager.")

            self.outputbox("Attempting to kill process.")
            stdout = self.sshobj.send_cmd(
                'ps aux | grep -v grep | grep "/opt/numeca/fine131/LINUX/euranus/euranusTurbox86_64" | grep "[f]ine" | grep "' + self.box_DISPLAY.text() + '"' + " | awk '{print $2}'")
            if stdout == "":
                self.outputbox("No running processes found.")
                return
            else:
                process_list = stdout.split('\n')
                # kill all euranusTurbo processes (multicore)
                for i in process_list:
                    if i != '':
                        stdout = self.sshobj.send_cmd("kill " + str(i))
                        self.outputbox("Killed fine EuranusTurbo (" + str(i) + ").")

        except AttributeError:
            self.outputbox("Error killing the process.")


class OptimPlotMassflow(FigureCanvas):
    """
    Real-Time plot of data from .res file.
    """

    def __init__(self, parent=None, width=4, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Massflow Inlet/Outlet")
        self.ax.set_xlabel("iteration")
        self.ax.set_ylabel("Massflow [kg/s]")
        # self.ax.legend()
        self.ax.grid()
        self.xlim = (0, 0)
        self.ylim = (0, 0)

        fig.set_tight_layout(True) # prevents clipping of ylabel
        ani = animation.FuncAnimation(fig, self.animate_massflow, interval=1000)

    def animate_massflow(self, ds):
        xs = []
        inlet = []
        outlet = []
        for key, val in ds.items():
            xs.append(int(key))
            inlet.append(float(val[8]))
            outlet.append(float(val[9]))

        self.ax.plot(xs, inlet, label="Inlet", color='royalblue')
        self.ax.plot(xs, outlet, label="Outlet", color='indianred')
        self.ax.legend(["Inlet", "Outlet"])
        self.ax.set_title("Massflow Inlet/Outlet")
        self.ax.set_xlabel("iteration")
        self.ax.set_ylabel("Massflow [kg/s]")
        self.ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

        # draw a vertical line @ 100 iterations to mark initialization
        if len(ds) == 100:
            self.ax.axvline(100, alpha=0.3)
        self.draw()

    def clear(self):
        self.ax.clear()
        self.ax.grid()
        self.ax.legend()


class OptimPlotXMF(FigureCanvas):
    """
    Real-Time plot of data from xmf file.
    """

    def __init__(self, parent=None, width=5, height=5, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(r'$c_p, \omega, \beta$')
        self.ax.set_xlabel("iteration")
        self.ax.set_ylabel(r"$c_p, \omega$")
        # self.ax.legend()
        self.ax.grid()
        self.xlim = (0, 0)
        self.ylim = (0, 0)

        self.ax2 = self.ax.twinx()
        self.ax2.set_ylabel(r"$\beta$", color='royalblue')

        fig.set_tight_layout(True) # prevents clipping of ylabel
        ani = animation.FuncAnimation(fig, self.animate_xmf, interval=1000)

    def animate_xmf(self, ds):
        xs = np.array(ds['i'])
        # velocities
        y_vel = np.array(ds['y_velocity'])
        z_vel = np.array(ds['z_velocity'])
        p_stat = np.array(ds['static_pressure'])
        p_atot = np.array(ds['abs_total_pressure'])

        # beta = np.arcsin(y_vel/z_vel)
        beta = np.array(
            list(map(lambda y, z: np.arcsin(y[1] / z[1]) if (z[1] > 1) and (y[1] > 1) else 0, y_vel, z_vel)))
        cp = np.array(
            list(map(lambda ps, pt: (ps[1] - ps[0]) / (pt[0] - ps[0]) if np.abs(
                (ps[1] - ps[0]) / (pt[0] - ps[0])) < 1 else 0,
                     p_stat, p_atot)))
        omega = np.array(
            list(map(lambda ps, pt: (pt[0] - pt[1]) / (pt[0] - ps[0]) if np.abs(
                (pt[0] - pt[1]) / (pt[0] - ps[0])) < 1 else 0,
                     p_stat, p_atot)))
        # self.ax.plot(xs, beta, color='royalblue', label='beta')
        self.ax.plot(xs, cp, color='indianred', label='cp')
        self.ax.plot(xs, omega, color='darkred', label='omega')
        self.ax.set_title(r'$c_p, \omega, \beta$')

        self.ax.set_xlabel("iteration")
        self.ax.set_ylabel(r"$c_p, \omega$")
        self.ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

        # ax2 = self.ax.twinx()
        self.ax2.set_ylabel(r"$\beta$", color='royalblue')
        self.ax2.plot(xs, np.rad2deg(beta), color='royalblue', label='beta')
        self.ax2.tick_params(axis='y', labelcolor='royalblue')
        self.ax.legend([r"$c_p$", r"$\omega$", r"$\beta$"])

        self.draw()

    def clear(self):
        self.ax.clear()
        self.ax.grid()
        self.ax.legend()
