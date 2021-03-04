import sys, os
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import QSizePolicy
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt as qt
from pyface.qt import QtGui
import cgitb

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from module.blade.bladetools import load_config_file
from module.UI.initialize import Initialize
from module.UI.blade.bladedesigner_handle import BDUpdateHandler
from module.UI.file_explorer import FileExplorer
from module.UI.blade.camber_spline_ui import CamberSplineUi
from module.UI.blade.thdist_spline_ui import ThdistSplineUi
from module.UI.blade.annulus_ui import AnnulusUi
from module.UI.ssh_login_ui import SSHLoginUi
from module.UI.save_load_config import SaveLoadConfig
from module.UI.optimizer.optimizer_handle import OptimHandler
from module.optimizer.optimizer_loadblade import LoadBlade
from module.UI.optimizer.deap_config_ui import DeapConfigUi
from module.UI.optimizer.three_point_settings_ui import ThreePointSettingsUI
from module.UI.optimizer.run_handle import RunHandler
from module.UI.optimizer.deap_run_handle import DeapRunHandler
from module.UI.blade.blade_plots import bladePlot

cgitb.enable(format='text')


class Ui(QtWidgets.QMainWindow, BDUpdateHandler, OptimHandler, FileExplorer, Initialize, SaveLoadConfig, LoadBlade,
         RunHandler, DeapRunHandler):
    """
        Load UI from .ui file (QT Designer). Load restraints for parameters (min, max, default, step) from
        restraints.txt. Parametee linked, so change one will modify the other (and vice versa).
    """

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('UI/qtdesigner/mainwindow.ui', self)
        self.VERSION = "0.1"

        # declaring param keys, load restraints for slider
        self.param_keys = ['alpha1', 'alpha2', 'lambd', 'th', 'xmax_th', 'xmax_camber', 'gamma_te', 'th_le',
                           'th_te', 'dist_blades', 'PP', 'AO']
        self.restraints = load_config_file('UI/config/restraints.txt')
        self.menu_default()  # set menu defaults
        self.init_variables()  # initialize some variables at GUI start
        self.init_slider_control()

        # see silent exception messages on crash
        sys._excepthook = sys.excepthook

        def exception_hook(exctype, value, traceback):
            print(exctype, value, traceback)
            sys._excepthook(exctype, value, traceback)
            sys.exit(1)

        sys.excepthook = exception_hook

        # tabs
        self.tabWidget.setTabText(0, "BladeDesigner")
        self.tabWidget.setTabText(1, "Optimizer")
        self.tabWidget.setCurrentIndex(1)  # set default tab

        # init plot
        self.m = PlotCanvas(self, width=8, height=10)
        toolbar = NavigationToolbar(self.m, self)
        centralwidget = self.fig_widget
        vbl = QtGui.QVBoxLayout(centralwidget)
        vbl.addWidget(toolbar)
        vbl.addWidget(self.m)

        # link buttons
        self.btn_update_all.clicked.connect(self.update_all)
        self.btn_update_sel.clicked.connect(self.update_select)
        self.reset = self.findChild(QtWidgets.QPushButton, 'btn_default')
        self.reset.clicked.connect(self.set_default)
        self.btn_hide_import.clicked.connect(self.update_imported_blade)

        # radio
        self.radio_blade1.toggled.connect(self.update_radio_blades)

        # menu
        self.thdist_V1.triggered.connect(self.update_thdist_V1)
        self.thdist_V2.triggered.connect(self.update_thdist_V2)
        self.nblades_single.triggered.connect(self.update_nblades_single)
        self.nblades_tandem.triggered.connect(self.update_nblades_tandem)
        self.actionAnnulus.triggered.connect(self.annulus_window)
        self.actionload_from_file.triggered.connect(self.openFileNameDialog)
        self.actionsave_as_txt.triggered.connect(self.saveFileDialog)
        self.actionCredential.triggered.connect(self.ssh_config_window)

        # save/load blade config
        self.actionSave_config.triggered.connect(self.save_config)
        self.actionLoad_config.triggered.connect(self.load_config)

        """ Camber Spline window """
        # open camber spline popup on click
        self.btn_spline_camber.clicked.connect(self.camber_spline_window)
        # get camber spline values from window
        self.returned_values.textChanged.connect(self.get_spline_pts)

        """ Thickness Spline window """
        # open camber spline popup on click
        self.btn_spline_th.clicked.connect(self.thdist_spline_window)

        # get camber spline values from window
        self.returned_values_th.textChanged.connect(self.get_spline_th_pts)

        self.update_in_control_vis(0)
        self.btn_in_up.clicked.connect(self.update_in_up)
        self.btn_in_down.clicked.connect(self.update_in_down)
        self.btn_in_left.clicked.connect(self.update_in_left)
        self.btn_in_right.clicked.connect(self.update_in_right)

        """ Optimizer links """
        # init deap config window
        self.deap_config_ui = DeapConfigUi()

        # open 3Point settings
        self.three_point_settings_ui = ThreePointSettingsUI()
        self.btn_3point_settings.clicked.connect(self.three_point_settings_window)

        # optimizer inits
        self.optim_handler_init()

        # run once on startup
        # load default blades
        self.update_all()
        self.load_config(Path(os.getcwd() + '/UI/config/default_blade.csv'))
        self.update_select()
        self.select_blade = 2
        self.update_select()
        # self.select_blade = 1

        self.show()

    def get_spline_pts(self, value):
        """
        Method is called when invisible Label with data from the spline window is being updated. Get Points from string.

        :param value: Value with coords of spline points
        :type value: str
        :return:
        """
        value = value.split(';')
        points = np.zeros((5, 2))
        for i, line in enumerate(value):
            val_splt = line.split(',')
            points[i, 0] = float(val_splt[0])
            points[i, 1] = float(val_splt[1])

        self.camber_spline_pts = points
        # print('main\n' + str(self.points))

    def get_spline_th_pts(self, value):
        """
        Method is called when invisible Label with data from the spline window is being updated. Get Points from string.

        :param value: Value with coords of spline points
        :type value: str
        :return:
        """
        value = value.split(';')
        points = np.zeros((5, 2))
        for i, line in enumerate(value):
            val_splt = line.split(',')
            points[i, 0] = float(val_splt[0])
            points[i, 1] = float(val_splt[1])

        self.points_th = points
        # print('main\n' + str(self.points))

    def ssh_config_window(self):
        """
        Opens Popup for login into putty.
        """
        self.login_ui = SSHLoginUi()
        self.login_ui.show()

    def deap_config_window(self):
        """
        Opens Popup for DEAP config.
        """
        self.deap_config_ui.show()

    def three_point_settings_window(self):
        self.three_point_settings_ui.show()

    def camber_spline_window(self):
        """
        Opens an additional spline window on when button 'Spline' has been clicked.
        :return:
        """
        self.cspline_ui = CamberSplineUi(self.ds, self.returned_values)
        self.cspline_ui.show()
        self.camber_spline_pts = self.cspline_ui.points

    def thdist_spline_window(self):
        """
        Opens an additional spline window on when button 'Spline' has been clicked.
        :return:
        """
        self.tspline_ui = ThdistSplineUi(self.ds, self.returned_values_th)
        self.tspline_ui.show()
        self.thdist_spline_pts = self.tspline_ui.points

    def annulus_window(self):
        """
        Opens an additional spline window on when button 'Spline' has been clicked.
        :return:
        """
        try:
            blades_from_plot = self.m._return_blades()
            self.annulus_ui = AnnulusUi(blades_from_plot, [self.ds1['x_offset'], self.ds1['y_offset']])
            self.annulus_ui.show()
        except AttributeError:
            print("Plot first.")

    def menu_default(self):
        self.thdist_ver = 1
        self.nblades = 'tandem'
        self.radio_blade1.setHidden(False)
        self.radio_blade1.setChecked(True)
        self.select_blade = 1
        self.radio_blade2.setHidden(False)
        self.btn_update_sel.setHidden(False)
        self.btn_update_all.setEnabled(False)

    def outputbox(self, msg):
        """
        Terminal in Optimizer window at the bottom.
        """

        datetimeobj = datetime.now()
        ts_str = datetimeobj.strftime("[%H:%M:%S]   ")
        self.box_terminal.append(ts_str + msg)
        self.box_terminal.moveCursor(QtGui.QTextCursor.End)


class PlotCanvas(FigureCanvas):
    """
    All the plotting commands are organized here. At GUI start, an empty empty figure is generated. On Update,
    BladeGen will be called with the user parameter and the plot will be updated.
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        # self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.ax = self.figure.add_subplot(111)
        self.xlim = (0, 0)
        self.ylim = (0, 0)

        # self.plot()

    def plot(self, ds, ds1=0, ds2=0, ds_import=0):
        if ds1 != 0:
            if type(ds_import) != int:
                bladePlot(self.ax, ds, ds1, ds2, ds_import)
            else:
                bladePlot(self.ax, ds, ds1, ds2)
        else:
            bladePlot(self.ax, ds)

        self.draw()

    def _return_blades(self):
        """Returns DataFrame of blades"""

        return self.plt_df


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.setAttribute(qt.WA_DeleteOnClose)
    app.exec_()
