from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets, uic
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from bladetools import load_restraints

import random

class Ui(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('qtdesigner/mainwindow_v1.ui', self)
        self.m = PlotCanvas(self, width=5, height=4)
        self.m.move(500, 20)
        self.update = self.findChild(QtWidgets.QPushButton, 'update_button') # find the button
        self.update.clicked.connect(self.update_inputs)
        self.scale = 100000
        self.restraints = load_restraints('restraints.txt')
        self.slider_control()
        self.show()

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
            self.set_restraint(self.slider[key], self.restraints[key], self.label[key])
            # self.slider[key].valueChanged.connect(self.label[key].setNum)


    def set_restraint(self, slider, restraint, label):
        """
        Set min, max, default and link to label
        :param slider:
        :param label:
        :param restraint:
        :return:
        """
        minval = restraint[0]
        maxval = restraint[1]
        step = restraint[2]
        defaultval = restraint[3]

        if (maxval >1):
            slider.setMinimum(minval)
            slider.setMaximum(maxval)
            slider.setSingleStep(step)
            slider.setValue(defaultval)
            slider.valueChanged.connect(label.setNum)
        else:
            slider.setMinimum(minval*self.scale)
            slider.setMaximum(maxval*self.scale)
            slider.setSingleStep(step*self.scale)
            slider.setValue(defaultval*self.scale)
            # fixme: display correct float value
            slider.valueChanged.connect(label.setNum)


    def update_inputs(self):
        # m = PlotCanvas(self, width=5, height=4)
        # m.move(500, 20)
        self.m.plot()
        print('button pressed')

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
        self.plot()

    def plot(self):
        data = [random.random() for i in range(25)]

        self.ax.plot(data, 'r-')
        self.ax.set_title('PyQt Matplotlib Example')
        self.draw()




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()