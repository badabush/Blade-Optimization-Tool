import numpy as np
from pathlib import Path
import os


class GeomTurboFile:

    def __init__(self, path, type, blade, r, l, N):
        """
        :param type: single or tandem
        :type type: str
        :param blade: list with array of single blade or list of arrays for tandem blades, cols: r, y, x
        :type blade: list
        :param r: ?
        :param l: ?
        :param N: number of blades
        """
        filename = "testgeo.geomTurbo"
        # Path to templates and file-saving folder
        self.temp_path = Path(os.getcwd() + "/optimizer/template/")
        self.save_path = Path(path)
        self.r = r
        self.l = l
        self.N = str(N)
        self.periodicity = str(0.024)
        self.type = type

        self.npts = 100
        self.scale = 25
        self.spacing = [0.0005, 0.02]
        self.zhub = np.linspace(0 - l / 3, 0 + 2 * l / 3, self.npts)

        if self.type == "single":
            self.layer = 0.0016
        elif self.type == "tandem":
            self.layer = 0.0010

        # compute parameters for file
        self.rh = self.r - self.layer / 2
        self.rs = self.r + self.layer / 2
        self.rhub = np.ones(self.npts) * self.rh
        self.rshroud = np.ones(self.npts) * self.rs

        self.hub = np.zeros((self.npts, 2))
        self.hub[:, 0] = self.zhub
        self.hub[:, 1] = self.rhub

        self.shroud = np.zeros((self.npts, 2))
        self.shroud[:, 0] = self.zhub
        self.shroud[:, 1] = self.rshroud

        # Generate file from parameters
        if self.type == "single":
            # fname = "single.geomTurbo"
            fname = filename
            self.gen_file(fname, blade[0])
        else:
            # fname = "tandem.geomTurbo"
            fname = filename
            self.gen_file(fname, blade[0], blade[1])

    def gen_file(self, fname, blade, blade_av=0):
        """
        Generating geomTurbo file for Single or tandem blade from Template.

        :param fname: filename.geomTurbo
        :type fname: str
        :param blade: single blade or tandem blade 1
        :type blade: np.array
        :param blade_av: tandem blade 2 (optional)
        :type blade_av: np.array
        """
        # # flip blade

        # blade[:,1] = blade[:,1] * -1
        # blade[:,2] = blade[:,2] * -1
        #
        # blade_av[:,1] = blade_av[:,1] * -1
        # blade_av[:,2] = blade_av[:,2] * -1

        len_blade = int(np.ceil(blade.shape[0] / 2) + 1)
        if self.type == "single":
            f = open(self.temp_path / "single_template.geomTurbo", "r")
        else:
            f = open(self.temp_path / "tandem_template.geomTurbo", "r")
        f_str = f.read()

        # HUBCURVE
        str_hubcurve = ""
        str_hubcurve = "".join(
            str_hubcurve + "   %.16f\t%.16f\n" % (self.hub[i, 0], self.hub[i, 1]) for i in range(self.npts))
        str_hubcurve = "%d\n" % (self.npts) + str_hubcurve
        f_str = f_str.replace("?IN_HUBCURVE", str_hubcurve[:-1])  # replace, get rid of trailing \n

        # SHROUD
        str_shroud = ""
        str_shroud = "".join(
            str_shroud + "   %.16f\t%.16f\n" % (self.shroud[i, 0], self.shroud[i, 1]) for i in range(self.npts))
        str_shroud = "%d\n" % (self.npts) + str_shroud
        f_str = f_str.replace("?IN_SHROUD", str_shroud[:-1])  # replace, get rid of trailing \n

        # upper (Saugseite)
        upper = np.zeros((len_blade, 3))
        upper[:, 1] = blade[len_blade - 2:, 1] / self.scale
        upper[:, 2] = blade[len_blade - 2:, 2] / self.scale
        # upper = upper[::-1]

        # upper section 1
        upper[:, 0] = self.rh
        str_upper1 = ""
        str_upper1 = "".join(
            str_upper1 + "   %.16f\t%.16f\t%.16f\n" % (upper[i, 0], upper[i, 1], upper[i, 2]) for i in
            range(len(upper)))
        str_upper1 = "%d\n" % (len(upper)) + str_upper1
        f_str = f_str.replace("?IN_UPPER1", str_upper1[:-1])  # replace, get rid of trailing \n

        # upper section 2
        upper[:, 0] = self.rs
        str_upper2 = ""
        str_upper2 = "".join(
            str_upper2 + "   %.16f\t%.16f\t%.16f\n" % (upper[i, 0], upper[i, 1], upper[i, 2]) for i in
            range(len(upper)))
        str_upper2 = "%d\n" % (len(upper)) + str_upper2
        f_str = f_str.replace("?IN_UPPER2", str_upper2[:-1])  # replace, get rid of trailing \n

        # lower (Druckseite)
        lower = np.zeros((len_blade - 1, 3))
        lower[:, 1] = blade[:len_blade - 1, 1] / self.scale
        lower[:, 2] = blade[:len_blade - 1, 2] / self.scale
        lower = lower[::-1]

        # lower section 1
        lower[:, 0] = self.rh
        str_lower1 = ""
        str_lower1 = "".join(
            str_lower1 + "   %.16f\t%.16f\t%.16f\n" % (lower[i, 0], lower[i, 1], lower[i, 2]) for i in
            range(len(lower)))
        str_lower1 = "%d\n" % (len(lower)) + str_lower1
        f_str = f_str.replace("?IN_LOWER1", str_lower1[:-1])  # replace, get rid of trailing \n

        # lower section 2
        lower[:, 0] = self.rs
        str_lower2 = ""
        str_lower2 = "".join(
            str_lower2 + "   %.16f\t%.16f\t%.16f\n" % (lower[i, 0], lower[i, 1], lower[i, 2]) for i in
            range(len(lower)))
        str_lower2 = "%d\n" % (len(lower)) + str_lower2
        f_str = f_str.replace("?IN_LOWER2", str_lower2[:-1])  # replace, get rid of trailing \n

        # Number of blades FV
        f_str = f_str.replace("?NOB_FV", self.N)
        f_str = f_str.replace("?PERIODICITY", self.periodicity)

        # TANDEM specific addins
        if self.type == "tandem":
            # upper (Saugseite)
            upper = np.zeros((len_blade, 3))
            upper[:, 1] = blade_av[len_blade - 2:, 1] / self.scale + self.spacing[0]
            upper[:, 2] = blade_av[len_blade - 2:, 2] / self.scale + self.spacing[1]
            # upper = upper[::-1]
            # upper section 1
            upper[:, 0] = self.rh
            str_upper1 = ""
            str_upper1 = "".join(
                str_upper1 + "   %.16f\t%.16f\t%.16f\n" % (upper[i, 0], upper[i, 1], upper[i, 2]) for i in
                range(len(upper)))
            str_upper1 = "%d\n" % (len(upper)) + str_upper1
            f_str = f_str.replace("?IN_UPPERAV1", str_upper1[:-1])  # replace, get rid of trailing \n

            # upper section 2
            upper[:, 0] = self.rs
            str_upper2 = ""
            str_upper2 = "".join(
                str_upper2 + "   %.16f\t%.16f\t%.16f\n" % (upper[i, 0], upper[i, 1], upper[i, 2]) for i in
                range(len(upper)))
            str_upper2 = "%d\n" % (len(upper)) + str_upper2
            f_str = f_str.replace("?IN_UPPERAV2", str_upper2[:-1])  # replace, get rid of trailing \n

            # lower (Druckseite)
            lower = np.zeros((len_blade - 1, 3))
            lower[:, 1] = blade_av[:len_blade-1, 1] / self.scale + self.spacing[0]
            lower[:, 2] = blade_av[:len_blade-1, 2] / self.scale + self.spacing[1]
            lower = lower[::-1]

            # lower section 1
            lower[:, 0] = self.rh
            str_lower1 = ""
            str_lower1 = "".join(
                str_lower1 + "   %.16f\t%.16f\t%.16f\n" % (lower[i, 0], lower[i, 1], lower[i, 2]) for i in
                range(len(lower)))
            str_lower1 = "%d\n" % (len(lower)) + str_lower1
            f_str = f_str.replace("?IN_LOWERAV1", str_lower1[:-1])  # replace, get rid of trailing \n

            # lower section 2
            lower[:, 0] = self.rs
            str_lower2 = ""
            str_lower2 = "".join(
                str_lower2 + "   %.16f\t%.16f\t%.16f\n" % (lower[i, 0], lower[i, 1], lower[i, 2]) for i in
                range(len(lower)))
            str_lower2 = "%d\n" % (len(lower)) + str_lower2
            f_str = f_str.replace("?IN_LOWERAV2", str_lower2[:-1])  # replace, get rid of trailing \n

            # number of blades
            f_str = f_str.replace("?NOB_AV", self.N)

        # replace tabspace with 8 whitespaces TODO: check if it works without this cleanup
        f_str = f_str.replace("\t\t", "        ")
        fsave = open(self.save_path / fname, "w")
        fsave.write(f_str)


if __name__ == "__main__":
    blade = np.zeros((600, 3))  # dummy data
    blade[:, 1] = np.linspace(0, 1, 600)
    blade[:, 2] = np.linspace(-1, 0, 600)
    foo = GeomTurboFile("path", "tandem", [blade, blade], 1, 1, 1)
