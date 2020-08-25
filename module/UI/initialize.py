import numpy as np
from module.blade.bladetools import load_config_file


class Initialize:
    """
    Everything regarding labels and Slider are handled here (connecting Slider and Labels, setting restraints).
    """

    def init_variables(self):
        """
        Initialize variables at GUI start
        """
        init_val = load_config_file("UI/config/init_values.csv")
        # Slider only accepts int values, so floats need to be scaled
        self.scale = init_val['scale']
        # points at GUI start are set to 9999, which initializes the default pattern for camber spline
        self.camber_spline_pts = np.ones((3, 2)) * 9999
        # offset for moving 2nd blade
        self.blade2_offset = [0, 0]  # X,Y
        self.in_blade_offset = [0, 0]
        self.imported_blade_vis = 0
        # fixed parameters since they wont be changed anyways
        self.length_chord = init_val['lchord']
        self.number_of_points = init_val['npts']
        self.state = 0

        # init points for camber and thickness spline
        self.camber_spline_pts = np.array([init_val['cspline_pts_x'], init_val['cspline_pts_y']]).T
        self.thdist_spline_pts = np.array([init_val['tspline_pts_x'], init_val['tspline_pts_y']]).T
        str_pts = "%f,%f;%f,%f;%f,%f;%f,%f;%f,%f" % (
            self.camber_spline_pts[0, 0], self.camber_spline_pts[0, 1],
            self.camber_spline_pts[1, 0], self.camber_spline_pts[1, 1],
            self.camber_spline_pts[2, 0], self.camber_spline_pts[2, 1],
            self.camber_spline_pts[3, 0], self.camber_spline_pts[3, 1],
            self.camber_spline_pts[4, 0], self.camber_spline_pts[4, 1])
        str_pts_th = "%f,%f;%f,%f;%f,%f;%f,%f;%f,%f" % (
            self.thdist_spline_pts[0, 0], self.thdist_spline_pts[0, 1],
            self.thdist_spline_pts[1, 0], self.thdist_spline_pts[1, 1],
            self.thdist_spline_pts[2, 0], self.thdist_spline_pts[2, 1],
            self.thdist_spline_pts[3, 0], self.thdist_spline_pts[3, 1],
            self.thdist_spline_pts[4, 0], self.thdist_spline_pts[4, 1])
        self.returned_values.setText(str_pts)
        self.returned_values_th.setText(str_pts_th)


    def init_slider_control(self):
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
        Set min, max, default and link to label. Boolean return indicates if data has float value (needs to be converted
        because labels only have integer steps).

        :param key: label/slider key
        :type key: str
        :return: bool
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
