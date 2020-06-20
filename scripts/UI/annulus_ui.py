from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, \
    QPushButton
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets, uic
from pyface.qt import QtGui, QtCore
import sys
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from scripts.bladetools import AnnulusGen
from bladetools import load_restraints

class AnnulusUi(QtWidgets.QMainWindow):

    def __init__(self, ds, offset):
        super(AnnulusUi, self).__init__()
        uic.loadUi('qtdesigner/annuluswindow.ui', self)
        self.restraints = load_restraints('config/restraints_annulus.txt')
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


        if self.ds['type'] == 'single':
            self.blade1, *_ = self.build_blades()
            _instance = AnnulusGen(self.nblades, self.r_inner, self.blade1)
            self.blade_list = _instance.generate()
        else:
            self.blade1, self.blade2 = self.build_blades()
            _instance = AnnulusGen(self.nblades, self.r_inner, self.blade1, self.blade2)
            self.blade_list = _instance.generate()

    def build_blades(self):
        "Reconstruct the blades from mainwindow."
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
        self.close()

    def reset_pts(self):
        self.points = np.array([[0, 0.25, 0.5, 0.75, 1], [0, 0.25, 0.5, 0.75, 1]]).T
        self.update_plot()

    def update_plot(self):
        # get spline
        self.r_inner = self.label_r.value()
        self.nblades = int(self.label_nblades.value())
        if self.ds['type'] == 'single':
            self.blade1, *_ = self.build_blades()
            _instance = AnnulusGen(self.nblades, self.r_inner, self.blade1)
            self.blade_list = _instance.generate()
        else:
            self.blade1, self.blade2 = self.build_blades()
            _instance = AnnulusGen(self.nblades, self.r_inner, self.blade1, self.blade2)
            self.blade_list = _instance.generate()
        self.m.plot(self.r_inner, self.blade_list)

    def update_nblades(self, value):
        self.label_nblades.setValue(value)

    def update_box_nblades(self):
        value = self.label_nblades.value()
        self.slider_nblades.setSliderPosition(value)

    def update_r(self, value):
        self.label_r.setValue(float(value) / self.scale)

    def update_box_r(self):
        value = self.label_r.value() * self.scale
        self.slider_r.setSliderPosition(value)

    def set_restraints(self, restraint, label, slider, scale=1):
        minval = restraint[0]
        maxval = restraint[1]
        step = restraint[2]
        defaultval = restraint[3]

        label.setMinimum(minval)
        label.setMaximum(maxval)
        label.setSingleStep(step)
        label.setValue(defaultval)
        slider.setMinimum(minval*scale)
        slider.setMaximum(maxval*scale)
        slider.setValue(defaultval*scale)



class PlotCanvas(FigureCanvas):

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

    def plot(self, r, blade_list):
        self.ax.cla()
        # print(pts)
        shape = blade_list.shape
        n2 = int(shape[0]/2)
        t = np.linspace(0, 2 * np.pi, shape[1])
        self.ax.plot(r * np.cos(t), r * np.sin(t), alpha=.5)
        [self.ax.plot(blade_list.iloc[:n2, i], blade_list.iloc[n2:, i], color='royalblue', alpha=.7) for i in
         range(shape[1])]
        self.ax.grid()
        self.ax.axis('equal')
        self.draw()
