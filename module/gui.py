from PyQt5.QtWidgets import QSizePolicy
from PyQt5 import QtWidgets, uic
from pyface.qt import QtGui
import sys
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from module.blade.bladetools import load_config_file
from module.blade.bladegen import BladeGen
from module.UI.initialize import Initialize
from module.UI.update_handle import UpdateHandler
from module.UI.file_explorer import FileExplorer
from module.UI.camber_spline_ui import CamberSplineUi
from module.UI.thdist_spline_ui import ThdistSplineUi
from module.UI.annulus_ui import AnnulusUi
from module.UI.putty_login_ui import PuttyLoginUi
from module.UI.save_load_config import SaveLoadConfig


class Ui(QtWidgets.QMainWindow, UpdateHandler, FileExplorer, Initialize, SaveLoadConfig):
    """
        Load UI from .ui file (QT Designer). Load restraints for parameters (min, max, default, step) from
        restraints.txt. Parameters with values or steps <1 have to be scaled since the slider only accepts int values.
        Slider and Textboxes are linked, so change one will modify the other (and vice versa).
        Plot will save zoom state even on updating plot.
    """

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('UI/qtdesigner/mainwindow.ui', self)
        # declaring param keys, load restraints for slider
        self.param_keys = ['alpha1', 'alpha2', 'lambd', 'th', 'xmax_th', 'xmax_camber', 'th_le',
                           'th_te', 'dist_blades']
        self.restraints = load_config_file('UI/config/restraints.txt')
        self.menu_default()  # set menu defaults
        self.init_variables()  # initialize some variables at GUI start
        self.init_slider_control()

        # tabs
        self.tabWidget.setTabText(0, "BladeDesigner")
        self.tabWidget.setTabText(1, "Optimizer")

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
        self.actionCredential.triggered.connect(self.putty_login_window)

        #save/load blade config
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

        self.update_b2_control_vis(0)
        self.update_in_control_vis(0)
        self.btn_b2_up.clicked.connect(self.update_B2_up)
        self.btn_b2_down.clicked.connect(self.update_B2_down)
        self.btn_b2_left.clicked.connect(self.update_B2_left)
        self.btn_b2_right.clicked.connect(self.update_B2_right)
        self.btn_in_up.clicked.connect(self.update_in_up)
        self.btn_in_down.clicked.connect(self.update_in_down)
        self.btn_in_left.clicked.connect(self.update_in_left)
        self.btn_in_right.clicked.connect(self.update_in_right)

        # run once on startup

        self.update_all()
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

    def putty_login_window(self):
        """
        Opens Popup for login into putty.
        """
        self.login_ui = PuttyLoginUi()
        self.login_ui.show()

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
            self.annulus_ui = AnnulusUi(blades_from_plot, [self.ds2['x_offset'], self.ds2['y_offset']])
            self.annulus_ui.show()
        except AttributeError:
            print("Plot first.")

    def menu_default(self):
        self.thdist_ver = 1
        self.nblades = 'single'
        self.radio_blade1.setHidden(True)
        self.radio_blade2.setHidden(True)
        self.btn_update_sel.setHidden(True)

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
        """
        Main window plot widget content. Differentiates between single/tandem, seperate control of tandem blades.

        :param ds: Data from single blade
        :type ds: pandas.DataFrame
        :param ds1: Data from 1st tandem blade, 0 if not specified
        :type ds1: pandas.DataFrame
        :param ds2: Data from 2nd tandem blade, 0 if not specified
        :type ds2: pandas.DataFrame
        :param ds_import: Data from imported blade, 0 if not specified
        :type ds_import: pandas.DataFrame
        :return: None
        """
        # get zoom state
        if self.xlim == (0, 0) and self.ylim == (0, 0):
            self.xlim = (-.1, 1)
            self.ylim = (-.1, 1)
        else:
            self.xlim = self.ax.get_xlim()
            self.ylim = self.ax.get_ylim()
        self.ax.cla()  # clear existing plots

        """
        Update Single Blade/Both blades at once with the same parameters
        """

        if ds['nblades'] == 'single':
            """Single blade"""
            bladegen = BladeGen(frontend='UI', nblade=ds['nblades'], th_dist_option=ds['thdist_ver'], npts=ds['npts'],
                                alpha1=ds['alpha1'], alpha2=ds['alpha2'],
                                lambd=ds['lambd'], th=ds['th'], x_maxth=ds['xmax_th'], x_maxcamber=ds['xmax_camber'],
                                l_chord=ds['l_chord'], th_le=ds['th_le'], th_te=ds['th_te'], spline_pts=ds['pts'],
                                thdist_points=ds['pts_th'])
            blade_data, camber_data = bladegen._return()
            division = ds['dist_blades'] * ds['l_chord']
            self.ax.plot(blade_data[:, 0], blade_data[:, 1], color='royalblue')
            self.ax.fill(blade_data[:, 0], blade_data[:, 1], color='cornflowerblue', alpha=.5)
            self.ax.plot(blade_data[:, 0], blade_data[:, 1] + division, color='royalblue')
            self.ax.fill(blade_data[:, 0], blade_data[:, 1] + division, color='cornflowerblue', alpha=.5)

            self.ax.plot(camber_data[::15, 0], camber_data[::15, 1], linestyle='--', dashes=(5, 5), color='darkblue')
            self.ax.plot(camber_data[::15, 0], camber_data[::15, 1] + division, linestyle='--', dashes=(5, 5),
                         color='darkblue', alpha=.7)
            self.plt_df = {'type': 'single', 'blade': blade_data, 'camber': camber_data}
        elif ds['nblades'] == 'tandem':
            """Tandem blades"""
            df_blades = {}
            # Update either both blades at once or blades seperately.
            dataselect = [ds1, ds2]
            for i in [0, 1]:
                df = dataselect[i]
                bladegen = BladeGen(frontend='UI', nblade=df['nblades'], th_dist_option=df['thdist_ver'],
                                    npts=df['npts'],
                                    alpha1=df['alpha1'], alpha2=df['alpha2'],
                                    lambd=df['lambd'], th=df['th'], x_maxth=df['xmax_th'],
                                    x_maxcamber=df['xmax_camber'],
                                    l_chord=df['l_chord'], th_le=df['th_le'], th_te=df['th_te'], spline_pts=df['pts'],
                                    thdist_points=df['pts_th'])
                blade_data, camber_data = bladegen._return()
                division = df['dist_blades'] * df['l_chord']
                # Update simultaneously
                blade1 = blade_data
                blade2 = np.copy(blade1)
                camber1 = camber_data
                camber2 = np.copy(camber_data)
                blade2[:, 0] = blade2[:, 0] + np.max(blade1[:, 0]) + .03 * (np.min(blade1[:, 0] + np.max(blade2[:, 0])))
                # blade2[:, 1] = blade2[:, 1] + (np.max(camber_data[:, 1]) - camber_data[0, 1]) - (
                #         1 - 0.915) * division / 10
                blade2[:, 1] = blade2[:, 1]
                camber2[:, 0] = camber2[:, 0] + np.max(camber1[:, 0]) + .03 * (
                    np.min(camber1[:, 0] + np.max(camber2[:, 0])))
                # camber2[:, 1] = camber2[:, 1] + (np.max(camber_data[:, 1]) - camber_data[0, 1]) - (
                #         1 - 0.915) * division / 10
                df_blades['blade1_%i' % (i + 1)] = blade1
                df_blades['blade2_%i' % (i + 1)] = blade2
                df_blades['camber1_%i' % (i + 1)] = camber1
                df_blades['camber2_%i' % (i + 1)] = camber2

            if ds['selected_blade'] == 0:
                """Update both blades at once"""
                self.ax.plot(blade1[:, 0], blade1[:, 1], color='royalblue')
                self.ax.fill(blade1[:, 0], blade1[:, 1], color='cornflowerblue', alpha=.5)
                self.ax.plot(camber1[::15, 0], camber1[::15, 1], linestyle='--', dashes=(5, 5), color='darkblue',
                             alpha=.7)

                self.ax.plot(blade2[:, 0] + ds2['x_offset'], blade2[:, 1]  + ds2['y_offset'], color='indianred')
                self.ax.fill(blade2[:, 0] + ds2['x_offset'], blade2[:, 1] + ds2['y_offset'], color='lightcoral', alpha=.5)
                self.ax.plot(camber2[::15, 0] + ds2['x_offset'], camber2[::15, 1] + ds2['y_offset'], linestyle='--', dashes=(5, 5), color='darkred',
                             alpha=.7)

                self.ax.plot(blade1[:, 0], blade1[:, 1] + division, color='royalblue')
                self.ax.fill(blade1[:, 0], blade1[:, 1] + division, color='cornflowerblue', alpha=.5)
                self.ax.plot(camber1[::15, 0], camber1[::15, 1] + division, linestyle='--', dashes=(5, 5),
                             color='darkblue', alpha=.7)
                self.ax.plot(blade2[:, 0] + ds2['x_offset'], blade2[:, 1] + division + ds2['y_offset'], color='indianred')
                self.ax.fill(blade2[:, 0] + ds2['x_offset'], blade2[:, 1] + division + ds2['y_offset'], color='lightcoral', alpha=.5)
                self.ax.plot(camber2[::15, 0] + ds2['x_offset'], camber2[::15, 1] + division + ds2['y_offset'], linestyle='--', dashes=(5, 5),
                             color='darkred', alpha=.7)

            else:
                """ Update blades seperately """
                self.ax.plot(df_blades['blade1_1'][:, 0], df_blades['blade1_1'][:, 1], color='royalblue')
                self.ax.fill(df_blades['blade1_1'][:, 0], df_blades['blade1_1'][:, 1], color='cornflowerblue', alpha=.5)
                self.ax.plot(df_blades['camber1_1'][::15, 0], df_blades['camber1_1'][::15, 1], linestyle='--',
                             dashes=(5, 5), color='darkblue', alpha=.7)
                self.ax.plot(df_blades['blade2_2'][:, 0] + ds2['x_offset'],
                             df_blades['blade2_2'][:, 1] + ds2['y_offset'], color='indianred')
                self.ax.fill(df_blades['blade2_2'][:, 0] + ds2['x_offset'],
                             df_blades['blade2_2'][:, 1] + ds2['y_offset'], color='lightcoral', alpha=.5)
                self.ax.plot(df_blades['camber2_2'][::15, 0] + ds2['x_offset'],
                             df_blades['camber2_2'][::15, 1] + ds2['y_offset'], linestyle='--',
                             dashes=(5, 5), color='darkred', alpha=.7)

                self.ax.plot(df_blades['blade1_1'][:, 0], df_blades['blade1_1'][:, 1] + division, color='royalblue')
                self.ax.fill(df_blades['blade1_1'][:, 0], df_blades['blade1_1'][:, 1] + division,
                             color='cornflowerblue', alpha=.5)
                self.ax.plot(df_blades['camber1_1'][::15, 0], df_blades['camber1_1'][::15, 1] + division,
                             linestyle='--', dashes=(5, 5), color='darkblue', alpha=.7)
                self.ax.plot(df_blades['blade2_2'][:, 0] + ds2['x_offset'],
                             df_blades['blade2_2'][:, 1] + division + ds2['y_offset'], color='indianred')
                self.ax.fill(df_blades['blade2_2'][:, 0] + ds2['x_offset'],
                             df_blades['blade2_2'][:, 1] + division + ds2['y_offset'], color='lightcoral',
                             alpha=.5)
                self.ax.plot(df_blades['camber2_2'][::15, 0] + ds2['x_offset'],
                             df_blades['camber2_2'][::15, 1] + division + ds2['y_offset'],
                             linestyle='--', dashes=(5, 5), color='darkred', alpha=.7)

                df_blades['type'] = 'tandem'
                self.plt_df = df_blades

        """ Plot imported blade if exists """
        try:
            self.ax.plot(ds_import.x + ds_import.x_offset, ds_import.y + ds_import.y_offset, 'r')
        except AttributeError:
            print("Error plotting imported blade.")
        self.ax.axis('equal')
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)
        self.ax.grid()
        self.draw()

    def _return_blades(self):
        """Returns DataFrame of blades"""

        return self.plt_df


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
