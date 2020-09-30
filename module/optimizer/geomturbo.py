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
        :param N: ?
        """
        filename = "testgeo.geomTurbo"
        # Path to templates and file-saving folder
        self.temp_path = Path(os.getcwd() + "/optimizer/template/")
        self.save_path = Path(path)
        self.r = r
        self.l = l
        self.N = N
        self.type = type

        self.npts = 100
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
            fname = "single.geomTurbo"
            fname = filename
            self.gen_file(fname, blade[0])
        else:
            fname = "tandem.geomTurbo"
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

        len_blade = blade.shape[0]
        if self.type == "single":
            f = open(self.temp_path / "single_template.geomTurbo", "r")
        else:
            f = open(self.temp_path / "tandem_template.geomTurbo", "r")
        f_str = f.read()

        # HUBCURVE
        str_hubcurve = ""
        str_hubcurve = "".join(
            str_hubcurve + "\t\t %.16f\t%.16f\n" % (self.hub[i, 0], self.hub[i, 1]) for i in range(self.npts))
        str_hubcurve = "\t\t +%d\n" % (self.npts) + str_hubcurve
        f_str = f_str.replace("?IN_HUBCURVE", str_hubcurve[:-1])  # replace, get rid of trailing \n

        # SHROUD
        str_shroud = ""
        str_shroud = "".join(
            str_shroud + "\t\t %.16f\t%.16f\n" % (self.shroud[i, 0], self.shroud[i, 1]) for i in range(self.npts))
        str_shroud = "\t\t +%d\n" % (self.npts) + str_shroud
        f_str = f_str.replace("?IN_SHROUD", str_shroud[:-1])  # replace, get rid of trailing \n

        # upper (Saugseite)
        upper = np.zeros((int(np.ceil(len_blade / 2)), 3))
        upper[:, 1] = blade[int(np.ceil(len_blade / 2)):, 1]
        upper[:, 2] = blade[int(np.ceil(len_blade / 2)):, 2]

        # upper section 1
        upper[:, 0] = self.rh
        str_upper1 = ""
        str_upper1 = "".join(
            str_upper1 + "\t\t %.16f\t%.16f\t%.16f\n" % (upper[i, 0], upper[i, 1], upper[i, 2]) for i in
            range(len(upper)))
        str_upper1 = "\t\t +%d\n" % (len(upper)) + str_upper1
        f_str = f_str.replace("?IN_UPPER1", str_upper1[:-1])  # replace, get rid of trailing \n

        # upper section 2
        upper[:, 0] = self.rs
        str_upper2 = ""
        str_upper2 = "".join(
            str_upper2 + "\t\t %.16f\t%.16f\t%.16f\n" % (upper[i, 0], upper[i, 1], upper[i, 2]) for i in
            range(len(upper)))
        str_upper2 = "\t\t +%d\n" % (len(upper)) + str_upper2
        f_str = f_str.replace("?IN_UPPER2", str_upper2[:-1])  # replace, get rid of trailing \n

        # lower (Druckseite)
        lower = np.zeros((int(np.ceil(len_blade / 2)), 3))
        lower[:, 1] = blade[:int(np.ceil(len_blade / 2)), 1]
        lower[:, 2] = blade[:int(np.ceil(len_blade / 2)), 2]
        lower = lower[::-1]

        # lower section 1
        lower[:, 0] = self.rh
        str_lower1 = ""
        str_lower1 = "".join(
            str_lower1 + "\t\t %.16f\t%.16f\t%.16f\n" % (lower[i, 0], lower[i, 1], lower[i, 2]) for i in
            range(len(lower)))
        str_lower1 = "\t\t +%d\n" % (len(lower)) + str_lower1
        f_str = f_str.replace("?IN_LOWER1", str_lower1[:-1])  # replace, get rid of trailing \n

        # lower section 2
        lower[:, 0] = self.rs
        str_lower2 = ""
        str_lower2 = "".join(
            str_lower2 + "\t\t %.16f\t%.16f\t%.16f\n" % (lower[i, 0], lower[i, 1], lower[i, 2]) for i in
            range(len(lower)))
        str_lower2 = "\t\t +%d\n" % (len(lower)) + str_lower2
        f_str = f_str.replace("?IN_LOWER2", str_lower2[:-1])  # replace, get rid of trailing \n

        # TANDEM specific addins
        if self.type == "tandem":
            # upper (Saugseite)
            upper = np.zeros((int(np.ceil(len_blade / 2)), 3))
            upper[:, 1] = blade_av[int(np.ceil(len_blade / 2)):, 1]
            upper[:, 2] = blade_av[int(np.ceil(len_blade / 2)):, 2]

            # upper section 1
            upper[:, 0] = self.rh
            str_upper1 = ""
            str_upper1 = "".join(
                str_upper1 + "\t\t %.16f\t%.16f\t%.16f\n" % (upper[i, 0], upper[i, 1], upper[i, 2]) for i in
                range(len(upper)))
            str_upper1 = "\t\t +%d\n" % (len(upper)) + str_upper1
            f_str = f_str.replace("?IN_UPPERAV1", str_upper1[:-1])  # replace, get rid of trailing \n

            # upper section 2
            upper[:, 0] = self.rs
            str_upper2 = ""
            str_upper2 = "".join(
                str_upper2 + "\t\t %.16f\t%.16f\t%.16f\n" % (upper[i, 0], upper[i, 1], upper[i, 2]) for i in
                range(len(upper)))
            str_upper2 = "\t\t +%d\n" % (len(upper)) + str_upper2
            f_str = f_str.replace("?IN_UPPERAV2", str_upper2[:-1])  # replace, get rid of trailing \n

            # lower (Druckseite)
            lower = np.zeros((int(np.ceil(len_blade / 2)), 3))
            lower[:, 1] = blade_av[:int(np.ceil(len_blade / 2)), 1]
            lower[:, 2] = blade_av[:int(np.ceil(len_blade / 2)), 2]
            lower = lower[::-1]

            # lower section 1
            lower[:, 0] = self.rh
            str_lower1 = ""
            str_lower1 = "".join(
                str_lower1 + "\t\t %.16f\t%.16f\t%.16f\n" % (lower[i, 0], lower[i, 1], lower[i, 2]) for i in
                range(len(lower)))
            str_lower1 = "\t\t +%d\n" % (len(lower)) + str_lower1
            f_str = f_str.replace("?IN_LOWERAV1", str_lower1[:-1])  # replace, get rid of trailing \n

            # lower section 2
            lower[:, 0] = self.rs
            str_lower2 = ""
            str_lower2 = "".join(
                str_lower2 + "\t\t %.16f\t%.16f\t%.16f\n" % (lower[i, 0], lower[i, 1], lower[i, 2]) for i in
                range(len(lower)))
            str_lower2 = "\t\t +%d\n" % (len(lower)) + str_lower2
            f_str = f_str.replace("?IN_LOWERAV2", str_lower2[:-1])  # replace, get rid of trailing \n

        # replace tabspace with 8 whitespaces TODO: check if it works without this cleanup
        f_str = f_str.replace("\t\t", "        ")
        fsave = open(self.save_path / fname, "w")
        fsave.write(f_str)


if __name__ == "__main__":
    blade = np.zeros((600, 3))  # dummy data
    blade[:, 1] = np.linspace(0, 1, 600)
    blade[:, 2] = np.linspace(-1, 0, 600)
    foo = GeomTurboFile("path", "tandem", [blade, blade], 1, 1, 1)
