from PyQt5.QtWidgets import QSizePolicy
from PyQt5 import QtWidgets, uic
from pyface.qt import QtGui
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from module.blade.bladetools import AnnulusGen, load_config_file


class AnnulusUi(QtWidgets.QMainWindow):

    def __init__(self, ds, offset):
        super(AnnulusUi, self).__init__()
        uic.loadUi('UI/qtdesigner/annuluswindow.ui', self)
        self.restraints = load_config_file('UI/config/restraints_annulus.txt')
        self.m = PlotCanvas(self, width=5, height=4)
        toolbar = NavigationToolbar(self.m, self)
        centralwidget = self.fig_widget
        vbl = QtGui.QVBoxLayout(centralwidget)
        vbl.addWidget(toolbar)
        vbl.addWidget(self.m)

        self.ds = ds
        self.offset = offset
        # init variables
        self.r_inner = .3
        self.nblades = 30
        self.scale = 100

        # restraints for widgets
        self.set_restraints(self.restraints['nblades'], self.label_nblades, self.slider_nblades)
        self.set_restraints(self.restraints['r'], self.label_r, self.slider_r, self.scale)

        # link label and slider
        self.label_r.editingFinished.connect(self.update_box_r)
        self.slider_r.valueChanged[int].connect(self.update_r)
        self.label_nblades.editingFinished.connect(self.update_box_nblades)
        self.slider_nblades.valueChanged[int].connect(self.update_nblades)

        self.btn_update.clicked.connect(self.update_plot)
        self.btn_close.clicked.connect(self.close_window)

        # TODO: seperating between single and tandem and the blade generation is obsolete (blade is a line in z-view),
        #  but might be useful if a 'z'-shape is required in the future

        if self.ds['type'] == 'single':
            self.blade1, *_ = self.build_blades()
            _instance = AnnulusGen(self.nblades, self.r_inner, self.blade1)
            self.blade_list = _instance.generate()
        else:
            self.blade1, self.blade2 = self.build_blades()
            _instance = AnnulusGen(self.nblades, self.r_inner, self.blade1, self.blade2)
            self.blade_list = _instance.generate()

    def build_blades(self):
        """
        Reconstruct the blades from mainwindow.
        """

        if self.ds['type'] == 'single':
            blade1 = self.ds['blade']
            return blade1, 0
        else:
            blade1 = self.ds['blade1_1']
            blade2 = self.ds['blade2_2']
            blade2[:, 0] = blade2[:, 0] + self.offset[0]
            blade2[:, 1] = blade2[:, 1] + self.offset[1]
            return blade1, blade2

    def close_window(self):
        """
        Close window on button click.
        """
        self.close()

    def update_plot(self):
        """
        Update Plot with input parameters.
        """
        # get spline
        self.r_inner = self.label_r.value()
        self.nblades = int(self.label_nblades.value() + 1)
        if self.ds['type'] == 'single':
            self.blade1, *_ = self.build_blades()
            _instance = AnnulusGen(self.nblades, self.r_inner, self.blade1)
            self.blade_list = _instance.generate()
        else:
            self.blade1, self.blade2 = self.build_blades()
            _instance = AnnulusGen(self.nblades, self.r_inner, self.blade1, self.blade2)
            self.blade_list = _instance.generate()
        # update dist label
        dist = np.abs(self.blade_list.iloc[0, 0] - self.blade_list.iloc[0, 1])
        self.update_dist(dist)
        # update plot
        self.m.plot(self.r_inner, self.blade_list)

    def update_nblades(self, value):
        """
        Update number of blades in label.

        :param value: value of label
        :type value: float
        """

        self.label_nblades.setValue(value)

    def update_box_nblades(self):
        """
        Update number of blades on slider.
        """
        value = self.label_nblades.value()
        self.slider_nblades.setSliderPosition(value)

    def update_r(self, value):
        """
        Update inner radius in label.

        :param value: value of label
        :type value: float
        """
        self.label_r.setValue(float(value) / self.scale)

    def update_box_r(self):
        """
        Update inner radius on slider.
        """

        value = self.label_r.value() * self.scale
        self.slider_r.setSliderPosition(value)

    def update_dist(self, value):
        """
        Update distance in label.

        :param value: value of label
        :type value: float
        """

        self.label_dist.setValue(value)

    def set_restraints(self, restraint, label, slider, scale=1.0):
        """
        Load restraints from file and apply to label and slider.

        :param restraint: from file, contains minval, maxval, steps, default
        :type restraint: list
        :param label: label of widget
        :type label: pyqt.Widget.label
        :param slider: slider of widget
        :type slider: pyqt.Widget.slider
        :param scale: scale to apply between float label and int slider (default=1)
        :type scale: float
        :return:
        """
        minval = restraint[0]
        maxval = restraint[1]
        step = restraint[2]
        defaultval = restraint[3]

        label.setMinimum(minval)
        label.setMaximum(maxval)
        label.setSingleStep(step)
        label.setValue(defaultval)
        slider.setMinimum(minval * scale)
        slider.setMaximum(maxval * scale)
        slider.setValue(defaultval * scale)


class PlotCanvas(FigureCanvas):
    """
    Class to handle Plot inside window. Very similar to main window plot.
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        # self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.ax = self.figure.add_subplot(111)
        self.xlim = (0, 0)
        self.ylim = (0, 0)

        # self.plot()

    def plot(self, r_inner, blade_list):
        """
        Method to handle all plotting tasks.

        :param r_inner: inner radius
        :type r_inner: float
        :param blade_list: list of blades with correct rotation and position to plot.
        :type blade_list: list
        :return:
        """
        self.ax.cla()
        # print(pts)
        shape = blade_list.shape
        n2 = int(shape[0] / 2)
        # line directly connecting blade edges
        t = np.linspace(0, 2 * np.pi, shape[1])
        # smooth circle at inner and outer edges
        t2 = np.linspace(0, 2 * np.pi, 100)
        self.ax.plot(r_inner * np.cos(t), r_inner * np.sin(t), 'k--', alpha=.3)
        self.ax.plot(r_inner * np.cos(t2), r_inner * np.sin(t2), color='cornflowerblue', alpha=.5)
        r_outer = r_inner + 1
        self.ax.plot(r_outer * np.cos(t), r_outer * np.sin(t), 'k--', alpha=.3)
        self.ax.plot(r_outer * np.cos(t2), r_outer * np.sin(t2), color='cornflowerblue', alpha=.5)
        self.ax.plot([blade_list.iloc[0, 0], blade_list.iloc[0, 1]], [blade_list.iloc[n2, 0], blade_list.iloc[n2, 1]], color='indianred', alpha=1)
        [self.ax.plot(blade_list.iloc[:n2, i], blade_list.iloc[n2:, i], color='royalblue', alpha=.7) for i in
         range(shape[1] - 1)]
        self.ax.grid()
        self.ax.axis('equal')
        self.draw()
