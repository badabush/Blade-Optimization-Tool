from PyQt5.QtWidgets import QSizePolicy
from PyQt5 import QtWidgets, uic
from pyface.qt import QtGui
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from blade.testspline import compute_spline
from blade.bladetools import load_config_file


class CamberSplineUi(QtWidgets.QMainWindow):

    def __init__(self, ds, main_value):
        super(CamberSplineUi, self).__init__()
        uic.loadUi('UI/qtdesigner/cambersplinewindow.ui', self)

        self.ds = ds
        self.main_value = main_value
        self.btn_close.clicked.connect(self.close_window)
        self.m = PlotCanvas(self, width=5, height=4)
        toolbar = NavigationToolbar(self.m, self)
        centralwidget = self.fig_widget
        vbl = QtGui.QVBoxLayout(centralwidget)
        vbl.addWidget(toolbar)
        vbl.addWidget(self.m)
        self.step = 0.05  # step to move on arrow click
        config_file = load_config_file('UI/config/init_values.csv')
        self.default_pts = [config_file['cspline_pts_x'], config_file['cspline_pts_y']]
        # init points
        # self.points = np.array([[0, 0.25, 0.5, 0.75, 1], [0, 0.25, 0.5, 0.75, 1]]).T
        try:
            self.get_spline_pts()
        except:
            self.points = np.array([self.default_pts[0], self.default_pts[1]]).T
        # run once on window open
        self.update_plot()

        # connect arrow buttons with spline movement
        self.p1_down.clicked.connect(self.update_p1_down)
        self.p1_up.clicked.connect(self.update_p1_up)
        self.p1_left.clicked.connect(self.update_p1_left)
        self.p1_right.clicked.connect(self.update_p1_right)

        self.p2_down.clicked.connect(self.update_p2_down)
        self.p2_up.clicked.connect(self.update_p2_up)
        self.p2_left.clicked.connect(self.update_p2_left)
        self.p2_right.clicked.connect(self.update_p2_right)

        self.p3_down.clicked.connect(self.update_p3_down)
        self.p3_up.clicked.connect(self.update_p3_up)
        self.p3_left.clicked.connect(self.update_p3_left)
        self.p3_right.clicked.connect(self.update_p3_right)

        # connect buttons for saving and resetting
        self.btn_save.clicked.connect(self._return)
        self.btn_reset.clicked.connect(self.reset_pts)

    def get_spline_pts(self):
        """
        Method is called when invisible Label with data from the spline window is being updated. Get Points from string.

        :param value: Value with coords of spline points
        :type value: str
        :return:
        """
        value = self.main_value.text().split(';')
        points = np.zeros((5, 2))
        for i, line in enumerate(value):
            val_splt = line.split(',')
            points[i, 0] = float(val_splt[0])
            points[i, 1] = float(val_splt[1])

        self.points = points

    def close_window(self):
        """
        Close Window.
        """
        self.close()

    def reset_pts(self):
        """
        Reset points back to default (straight line).
        """
        self.points = np.array([self.default_pts[0], self.default_pts[1]]).T
        self.update_plot()

    def _return(self):
        """
        Return Points back to main window by saving it to an invisible label.
        """
        print('returning values')
        str_pts = "%f,%f;%f,%f;%f,%f;%f,%f;%f,%f" % (
            self.points[0, 0], self.points[0, 1], self.points[1, 0], self.points[1, 1], self.points[2, 0],
            self.points[2, 1], self.points[3, 0], self.points[3, 1], self.points[4, 0], self.points[4, 1])
        self.main_value.setText(str_pts)
        self.close()

    def update_plot(self):
        """
        Update plot in spline window by calling the plot class with new points.
        """
        xy = compute_spline(self.points[:,0], self.points[:,1])

        self.m.plot(xy, self.points)

    # this is becoming very ugly again. Fix this as soon as shorter solution is found.
    # <P1>
    def update_p1_down(self):
        """
        Point 1 position control, button [down].
        """
        self.points[1, 1] = self.points[1, 1] - self.step
        self.update_plot()

    def update_p1_up(self):
        """
        Point 1 position control, button [up].
        """
        self.points[1, 1] = self.points[1, 1] + self.step
        self.update_plot()

    def update_p1_left(self):
        """
        Point 1 position control, button [left].
        """
        self.points[1, 0] = self.points[1, 0] - self.step
        self.update_plot()

    def update_p1_right(self):
        """
        Point 1 position control, button [right].
        """
        self.points[1, 0] = self.points[1, 0] + self.step
        self.update_plot()

    # </P1><P2>
    def update_p2_down(self):
        """
        Point 2 position control, button [down].
        """
        self.points[2, 1] = self.points[2, 1] - self.step
        self.update_plot()

    def update_p2_up(self):
        """
        Point 2 position control, button [up].
        """
        self.points[2, 1] = self.points[2, 1] + self.step
        self.update_plot()

    def update_p2_left(self):
        """
        Point 2 position control, button [left].
        """
        self.points[2, 0] = self.points[2, 0] - self.step
        self.update_plot()

    def update_p2_right(self):
        """
        Point 2 position control, button [right].
        """
        self.points[2, 0] = self.points[2, 0] + self.step
        self.update_plot()

    # </P2><P3>
    def update_p3_down(self):
        """
        Point 3 position control, button [down].
        """
        self.points[3, 1] = self.points[3, 1] - self.step
        self.update_plot()

    def update_p3_up(self):
        """
        Point 3 position control, button [up].
        """
        self.points[3, 1] = self.points[3, 1] + self.step
        self.update_plot()

    def update_p3_left(self):
        """
        Point 3 position control, button [left].
        """
        self.points[3, 0] = self.points[3, 0] - self.step
        self.update_plot()

    def update_p3_right(self):
        """
        Point 3 position control, button [right].
        """
        self.points[3, 0] = self.points[3, 0] + self.step
        self.update_plot()
    # </P3>


class PlotCanvas(FigureCanvas):
    """
    Class for Plotting inside of Spline Window. Very similar to main window plot class.
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

    def plot(self, xy, pts):
        """
        Method for handling all plotting tasks.
        :param xy: xy-coords of spline
        :type xy: np.array
        :param pts: Points on spline.
        :type pts: list
        :return:
        """

        self.ax.cla()
        # print(pts)
        self.ax.plot(xy[:, 0], xy[:, 1])
        self.ax.plot(pts[:, 0], pts[:, 1], 'go')
        self.ax.plot([0, 1], [0, 1], 'ro')
        self.ax.plot(np.arange(20) / 20, np.arange(20) / 20, 'k.', markersize=.5, alpha=.5)
        self.ax.grid()
        self.ax.axis('equal')
        self.draw()
