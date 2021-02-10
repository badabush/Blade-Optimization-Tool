import numpy as np

from PyQt5.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.ticker import MaxNLocator

from module.optimizer.optimtools import calc_xmf


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
        try:
            for key, val in ds.items():
                xs.append(int(key))
                inlet.append(float(val[8]))
                outlet.append(float(val[9]))
        except IndexError as e:
            print(e)
            return
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
        # self.ax.legend()


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

        # velocities
        beta, cp, omega = calc_xmf(ds)

        try:
            xs = np.array(ds['i'])
        except KeyError:
            xs = np.arange(cp.shape[0])

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
        lines = line1 + line2 + line3
        labels = [l.get_label() for l in lines]
        self.ax.legend(lines, labels)

        self.draw()

    def clear(self):
        self.ax.clear()
        self.ax.grid()
        # self.ax.legend()


class OptimPlotDEAP(FigureCanvas):
    """
    Real-Time plot of data from xmf file.
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
        self.ax.set_title(r'DEAP Generation/Min')
        self.ax.set_xlabel("generation")
        self.ax.set_ylabel("fitness")
        # self.ax.legend()
        self.ax.grid()
        self.xlim = (0, 0)
        self.ylim = (0, 0)

        fig.set_tight_layout(True)  # prevents clipping of ylabel
        ani = animation.FuncAnimation(fig, self.animate_deap, interval=1000)

    def animate_deap(self, ds):
        # gen = ds
        # fitmin = []
        #
        self.clear()
        self.ax.plot(np.arange(len(ds))+1, ds, color="indianred", label="fitness")
        self.ax.xaxis.set_major_locator(MaxNLocator(integer=True))  # force integer x values
        self.draw()

    def clear(self):
        self.ax.clear()
        self.ax.grid()
        self.ax.legend()
