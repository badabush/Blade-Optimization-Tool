import numpy as np

from PyQt5.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation
import matplotlib.pyplot as plt

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

        fig.set_tight_layout(True)  # prevents clipping of ylabel
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
        self.ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))

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

        fig.set_tight_layout(True)  # prevents clipping of ylabel
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

        line1 = self.ax.plot(xs, cp, color='indianred', label=r'$cp$')
        line2 = self.ax.plot(xs, omega, color='darkred', label=r'$\omega$')
        line3 = self.ax2.plot(xs, np.rad2deg(beta), color='royalblue', label=r'$beta$')
        self.ax.set_title(r'$c_p, \omega, \beta$')

        self.ax.set_xlabel("iteration")
        self.ax.set_ylabel(r"$c_p, \omega$")
        self.ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
        self.ax.tick_params(axis='y', labelcolor='darkred')

        self.ax2.set_ylabel(r"$\beta$", color='royalblue')
        self.ax2.tick_params(axis='y', labelcolor='royalblue')

        # combine legends
        lines = line1+line2+line3
        labels = [l.get_label() for l in lines]
        # self.ax.legend([r"$c_p$", r"$\omega$", r"$\beta$"])
        self.ax.legend(lines, labels)

        self.draw()

    def clear(self):
        self.ax.clear()
        self.ax.grid()
        self.ax.legend()
