from PyQt5.QtWidgets import QSizePolicy, QFileDialog
from PyQt5 import QtWidgets, uic
from pyface.qt import QtGui
import sys
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


from module.blade.bladetools import load_restraints
from module.blade.bladegen import BladeGen
from module.UI.update_handle import UpdateHandler
from module.UI.file_explorer import FileExplorer
from module.UI.spline_ui import SplineUi
from module.UI.spline_ui2 import SplineUi2
from module.UI.annulus_ui import AnnulusUi


class Ui(QtWidgets.QMainWindow, UpdateHandler, FileExplorer):
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
        self.param_keys = ['npts', 'alpha1', 'alpha2', 'lambd', 'th', 'xmax_th', 'xmax_camber', 'l_chord', 'th_le',
                           'th_te', 'dist_blades']
        self.restraints = load_restraints('UI/config/restraints.txt')
        self.menu_default()  # set menu defaults
        self.init_variables()  # initialize some variables at GUI start

        # init plot
        self.m = PlotCanvas(self, width=8, height=10)
        toolbar = NavigationToolbar(self.m, self)
        centralwidget = self.fig_widget
        vbl = QtGui.QVBoxLayout(centralwidget)
        vbl.addWidget(toolbar)
        vbl.addWidget(self.m)

        # link buttons
        self.btn_update_all.clicked.connect(self.update_inputs)
        self.btn_update_sel.clicked.connect(self.update_select)
        self.reset = self.findChild(QtWidgets.QPushButton, 'btn_default')
        self.reset.clicked.connect(self.set_default)

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
        self.slider_control()
        self.show()

        # init points
        self.points = np.array([[0, 0.25, 0.5, 0.75, 1], [0, 0.25, 0.5, 0.75, 1]]).T
        self.points_th = np.array([[0, 0.2, 0.4, 0.65, 1], [0, 0.45, 1.0, 0.25, 0]]).T
        str_pts = "%f,%f;%f,%f;%f,%f;%f,%f;%f,%f" % (
            self.points[0, 0], self.points[0, 1], self.points[1, 0], self.points[1, 1], self.points[2, 0],
            self.points[2, 1], self.points[3, 0], self.points[3, 1], self.points[4, 0], self.points[4, 1]) 
        str_pts_th = "%f,%f;%f,%f;%f,%f;%f,%f;%f,%f" % (
            self.points_th[0, 0], self.points_th[0, 1], self.points_th[1, 0], self.points_th[1, 1], self.points_th[2, 0],
            self.points_th[2, 1], self.points_th[3, 0], self.points_th[3, 1], self.points_th[4, 0], self.points_th[4, 1])
        self.returned_values.setText(str_pts)
        self.returned_values_th.setText(str_pts_th)

        # open spline popup on click
        self.btn_spline_camber.clicked.connect(self.spline_window)
        self.btn_spline_th.clicked.connect(self.spline_window2)

        # get spline values from 2nd window
        self.returned_values.textChanged.connect(self.get_spline_pts)
        self.returned_values_th.textChanged.connect(self.get_spline_th_pts)
        #
        #
        self.update_b2_control_vis(0)
        self.btn_b2_up.clicked.connect(self.update_B2_up)
        self.btn_b2_down.clicked.connect(self.update_B2_down)
        self.btn_b2_left.clicked.connect(self.update_B2_left)
        self.btn_b2_right.clicked.connect(self.update_B2_right)

        # run once on startup
        self.update_inputs()

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

        self.points = points
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

    def spline_window(self):
        """
        Opens an additional spline window on when button 'Spline' has been clicked.
        :return:
        """
        self.spline_ui = SplineUi(self.ds, self.returned_values)
        self.spline_ui.show()
        self.points = self.spline_ui.points

    def spline_window2(self):
        """
        Opens an additional spline window on when button 'Spline' has been clicked.
        :return:
        """
        self.spline_ui = SplineUi2(self.ds, self.returned_values_th)
        self.spline_ui.show()
        self.points = self.spline_ui.points

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

    def init_variables(self):
        """
        All variables that need to be defined at system start are gathered here.
        """
        # Slider only accepts int values, so floats need to be scaled
        self.scale = 100000
        # points at GUI start are set to 9999, which initializes the default pattern for camber spline
        self.points = np.ones((3, 2)) * 9999
        # offset for moving 2nd blade
        self.blade2_offset = [0, 0]  # X,Y

    def slider_control(self):
        """
        Setting up slider and linking to label.
        """
        self.slider = {}
        self.label = {}
        self.slider['alpha1'] = self.slider_alpha1
        self.label['alpha1'] = self.val_alpha1

        self.slider['alpha2'] = self.slider_alpha2
        self.label['alpha2'] = self.val_alpha2

        self.slider['lambd'] = self.slider_lambd
        self.label['lambd'] = self.val_lambd

        self.slider['th'] = self.slider_th
        self.label['th'] = self.val_th

        self.slider['xmax_th'] = self.slider_xmax_th
        self.label['xmax_th'] = self.val_xmax_th

        self.slider['xmax_camber'] = self.slider_xmax_camber
        self.label['xmax_camber'] = self.val_xmax_camber

        self.slider['th_le'] = self.slider_thle
        self.label['th_le'] = self.val_thle

        self.slider['th_te'] = self.slider_thte
        self.label['th_te'] = self.val_thte

        self.slider['l_chord'] = self.slider_lchord
        self.label['l_chord'] = self.val_lchord

        self.slider['npts'] = self.slider_npts
        self.label['npts'] = self.val_npts

        self.slider['dist_blades'] = self.slider_dist_blades
        self.label['dist_blades'] = self.val_dist_blades
        for key in self.slider:
            retval = self.set_restraint(key)
            if retval == 1:
                # set default values for floats
                self.label[key].setSingleStep(0.0001)
                self.label[key].setValue(self.restraints[key][3])

        # connect labels->slider
        self.label['alpha1'].editingFinished.connect(self.update_box_alpha1)
        self.label['alpha2'].editingFinished.connect(self.update_box_alpha2)
        self.label['lambd'].editingFinished.connect(self.update_box_lambd)
        self.label['l_chord'].editingFinished.connect(self.update_box_l_chord)
        self.slider['npts'].valueChanged[int].connect(self.update_npts)
        self.label['npts'].editingFinished.connect(self.update_box_npts)
        self.slider['th'].valueChanged[int].connect(self.update_th)
        self.label['th'].editingFinished.connect(self.update_box_th)
        self.slider['xmax_th'].valueChanged[int].connect(self.update_xmax_th)
        self.label['xmax_th'].editingFinished.connect(self.update_box_xmax_th)
        self.slider['xmax_camber'].valueChanged[int].connect(self.update_xmax_camber)
        self.label['xmax_camber'].editingFinished.connect(self.update_box_xmax_camber)
        self.slider['th_le'].valueChanged[int].connect(self.update_thle)
        self.label['th_le'].editingFinished.connect(self.update_box_thle)
        self.slider['th_te'].valueChanged[int].connect(self.update_thte)
        self.label['th_te'].editingFinished.connect(self.update_box_thte)
        self.slider['dist_blades'].valueChanged[int].connect(self.update_dist_blades)
        self.label['dist_blades'].editingFinished.connect(self.update_box_dist_blades)

    def set_restraint(self, key):
        """
        Set min, max, default and link to label
        :param slider: All existing slider with key from keylist.
        :type slider: dict
        :param label: All existing label wiht key from keylist.
        :type label: dict
        :param restraint:
        :return:
        """
        slider = self.slider[key]
        restraint = self.restraints[key]
        label = self.label[key]

        minval = restraint[0]
        maxval = restraint[1]
        step = restraint[2]
        defaultval = restraint[3]

        if (maxval > 1):
            label.setMinimum(minval)
            label.setMaximum(maxval)
            label.setSingleStep(step)
            label.setValue(defaultval)
            if key == 'npts':
                slider.setMinimum(minval / 100)
                slider.setMaximum(maxval / 100)
                slider.setValue(defaultval / 100)
            else:
                slider.setMinimum(minval)
                slider.setMaximum(maxval)
                slider.setTickInterval(step)
                slider.setValue(defaultval)
                slider.valueChanged[int].connect(label.setValue)
            return 0
        else:
            label.setMinimum(minval)
            label.setMaximum(maxval)
            label.setSingleStep(step)
            slider.setMinimum(minval * self.scale)
            slider.setMaximum(maxval * self.scale)
            slider.setSingleStep(step * self.scale)
            slider.setValue(defaultval * self.scale)
            return 1


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

    def plot(self, ds, ds1=0, ds2=0, blade_import=0):
        print(ds2)
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
                blade2[:,1] = blade2[:,1]
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

                self.ax.plot(blade2[:, 0], blade2[:, 1], color='indianred')
                self.ax.fill(blade2[:, 0], blade2[:, 1], color='lightcoral', alpha=.5)
                self.ax.plot(camber2[::15, 0], camber2[::15, 1], linestyle='--', dashes=(5, 5), color='darkred',
                             alpha=.7)

                self.ax.plot(blade1[:, 0], blade1[:, 1] + division, color='royalblue')
                self.ax.fill(blade1[:, 0], blade1[:, 1] + division, color='cornflowerblue', alpha=.5)
                self.ax.plot(camber1[::15, 0], camber1[::15, 1] + division, linestyle='--', dashes=(5, 5),
                             color='darkblue', alpha=.7)
                self.ax.plot(blade2[:, 0], blade2[:, 1] + division, color='indianred')
                self.ax.fill(blade2[:, 0], blade2[:, 1] + division, color='lightcoral', alpha=.5)
                self.ax.plot(camber2[::15, 0], camber2[::15, 1] + division, linestyle='--', dashes=(5, 5),
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
            self.ax.plot(blade_import.x, blade_import.y, 'r')
        except AttributeError:
            print("Error plotting imported blade.")
        self.ax.axis('equal')
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)
        self.ax.grid()
        self.draw()

    def plot_import(self, ds):
        x = ds.x
        y = ds.y
        self.ax.plot(x,y)

    def _return_blades(self):
        return self.plt_df


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
