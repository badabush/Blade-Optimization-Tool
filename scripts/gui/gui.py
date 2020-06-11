from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, \
    QPushButton
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets, uic
from pyface.qt import QtGui, QtCore
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from bladetools import load_restraints

import random
import math
from bladegen import BladeGen


class Ui(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('qtdesigner/mainwindow_v1.ui', self)
        # declaring param keys, load restraints for slider
        self.param_keys = ['npts', 'beta1', 'beta2', 'lambd', 'rth', 'xmax_th', 'xmax_camber', 'l_chord', 'th_le',
                           'th_te']
        self.restraints = load_restraints('restraints.txt')
        self.menu_default()
        # Slider only accepts int values, so floats need to be scaled
        self.scale = 100000
        # init plot
        self.m = PlotCanvas(self, width=5, height=4)
        toolbar = NavigationToolbar(self.m, self)
        centralwidget = self.fig_widget
        vbl = QtGui.QVBoxLayout(centralwidget)
        vbl.addWidget(toolbar)
        vbl.addWidget(self.m)
        self.m.move(500, 20)

        # link buttons
        self.update = self.findChild(QtWidgets.QPushButton, 'btn_update')
        self.update.clicked.connect(self.update_inputs)
        self.reset = self.findChild(QtWidgets.QPushButton, 'btn_default')
        self.reset.clicked.connect(self.set_default)
        self.thdist_V1.triggered.connect(self.update_thdist_V1)
        self.thdist_V2.triggered.connect(self.update_thdist_V2)
        self.slider_control()
        self.show()

    def menu_default(self):
        self.thdist_ver = 0

    def slider_control(self):

        self.slider = {}
        self.label = {}
        self.slider['beta1'] = self.slider_beta1
        self.label['beta1'] = self.val_beta1

        self.slider['beta2'] = self.slider_beta2
        self.label['beta2'] = self.val_beta2

        self.slider['lambd'] = self.slider_lambd
        self.label['lambd'] = self.val_lambd

        self.slider['rth'] = self.slider_rth
        self.label['rth'] = self.val_rth

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
        for key in self.slider:
            retval = self.set_restraint(key)
            if retval == 1:
                # set default values for floats
                self.label[key].setSingleStep(0.0001)
                self.label[key].setValue(self.restraints[key][3])

        # connect labels->slider
        self.label['beta1'].editingFinished.connect(self.update_box_beta1)
        self.label['beta2'].editingFinished.connect(self.update_box_beta2)
        self.label['lambd'].editingFinished.connect(self.update_box_lambd)
        self.label['l_chord'].editingFinished.connect(self.update_box_l_chord)
        self.slider['npts'].valueChanged[int].connect(self.update_npts)
        self.label['npts'].editingFinished.connect(self.update_box_npts)
        self.slider['rth'].valueChanged[int].connect(self.update_rth)
        self.label['rth'].editingFinished.connect(self.update_box_rth)
        self.slider['xmax_th'].valueChanged[int].connect(self.update_xmax_th)
        self.slider['xmax_camber'].valueChanged[int].connect(self.update_xmax_camber)
        self.slider['th_le'].valueChanged[int].connect(self.update_thle)
        self.slider['th_te'].valueChanged[int].connect(self.update_thte)

    def set_restraint(self, key):
        """
        Set min, max, default and link to label
        :param slider:
        :param label:
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

    """
    A very quick and dirty approach... Alternatively, creating a custom DoubleSlider class would be way cleaner.
    TODO: fix this when bored. 
    """

    def update_box_beta1(self):
        value = self.label['beta1'].value()
        self.slider['beta1'].setSliderPosition(value)

    def update_box_beta2(self):
        value = self.label['beta2'].value()
        self.slider['beta2'].setSliderPosition(value)

    def update_box_l_chord(self):
        value = self.label['l_chord'].value()
        self.slider['l_chord'].setSliderPosition(value)

    def update_box_lambd(self):
        value = self.label['lambd'].value()
        self.slider['lambd'].setSliderPosition(value)

    def update_npts(self, value):
        self.label['npts'].setValue(float(value) * 100)

    def update_box_npts(self):
        val_raw = self.label['npts'].value()
        if (val_raw % 100) > 50:
            value = math.ceil(val_raw / 100)
        else:
            value = math.floor(val_raw / 100)
        self.label['npts'].setValue(float(value) * 100)
        self.slider['npts'].setSliderPosition(value)

    def update_rth(self, value):
        self.label['rth'].setValue(float(value) / self.scale)

    def update_box_rth(self):
        value = self.label['rth'].value() * self.scale
        self.slider['rth'].setSliderPosition(value)

    def update_xmax_th(self, value):
        self.label['xmax_th'].setValue(float(value) / self.scale)

    def update_box_rth(self):
        value = self.label['xmax_th'].value() * self.scale
        self.slider['xmax_th'].setSliderPosition(value)

    def update_xmax_camber(self, value):
        self.label['xmax_camber'].setValue(float(value) / self.scale)

    def update_box_xmax_camber(self):
        value = self.label['xmax_camber'].value() * self.scale
        self.slider['xmax_camber'].setSliderPosition(value)

    def update_thle(self, value):
        if (float(value)/self.scale)<0.01 and (float(value)/self.scale)>0.0:
            self.label['th_le'].setValue(0.01)
        else:
            self.label['th_le'].setValue(float(value) / self.scale)

    def update_box_thle(self):
        value = self.label['th_le'].value() #* self.scale
        if value<0.01 and value>0.0:
            value = 0.01 * self.scale
        self.slider['th_le'].setSliderPosition(value)

    def update_thte(self, value):
        if (float(value) / self.scale) < 0.01 and (float(value) / self.scale) > 0.0:
            self.label['th_te'].setValue(0.01)
        else:
            self.label['th_te'].setValue(float(value) / self.scale)

    def update_box_thte(self):
        value = self.label['th_te'].value()  # * self.scale
        if value < 0.01 and value > 0.0:
            value = 0.01 * self.scale
        self.slider['th_te'].setSliderPosition(value)

    def update_inputs(self):
        # get values
        ds = {}
        for key in self.param_keys:
            ds[key] = self.label[key].value()
        ds['thdist_ver'] = self.thdist_ver
        self.m.plot(ds)
        print('Updating Plot')

    def set_default(self):
        # set values
        for key in self.param_keys:
            self.label[key].setValue(self.restraints[key][3])
            if key == 'npts':
                self.slider[key].setSliderPosition(self.restraints[key][3]/100)
            elif self.restraints[key][1] > 1:
                self.slider[key].setSliderPosition(self.restraints[key][3])
            else:
                self.slider[key].setSliderPosition(self.restraints[key][3] * self.scale)
        print('Resetting Values')

    def update_thdist_V1(self):
        self.thdist_ver = 0

    def update_thdist_V2(self):
        self.thdist_ver = 1

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.ax = self.figure.add_subplot(111)
        self.xlim = (0,0)
        self.ylim = (0,0)

        # self.plot()

    def plot(self, ds):
        # get zoom state
        if self.xlim == (0,0) and self.ylim == (0,0):
            self.xlim = (-0.05, 1)
            self.ylim = (-.2, .65)
        else:
            self.xlim = self.ax.get_xlim()
            self.ylim = self.ax.get_ylim()
        self.ax.cla() # clear existing plots
        bladegen = BladeGen(frontend='gui', th_dist_option=ds['thdist_ver'], npts=ds['npts'], beta1=ds['beta1'], beta2=ds['beta2'],
                            lambd=ds['lambd'], r_th=ds['rth'], x_maxth=ds['xmax_th'], x_maxcamber=ds['xmax_camber'],
                            l_chord=ds['l_chord'], rth_le=ds['th_le'], rth_te=ds['th_te'])
        blade_data = bladegen._return()
        self.ax.plot(blade_data[:, 0], blade_data[:, 1])
        # self.ax.fill_between(blade_data[:, 0], blade_data[:, 1], color='b')
        # self.ax.set_title('Blade')
        self.ax.axis('equal')
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)
        self.ax.grid()
        self.draw()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
