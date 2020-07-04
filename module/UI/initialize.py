class Initialize:
    """
    Everything regarding labels and Slider are handled here (connecting Slider and Labels, setting restraints).
    """

    def slider_control(self):
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

        self.slider['l_chord'] = self.slider_lchord
        self.label['l_chord'] = self.val_lchord

        self.slider['npts'] = self.slider_npts
        self.label['npts'] = self.val_npts

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
        self.label['l_chord'].editingFinished.connect(self.update_box_l_chord)
        self.slider['npts'].valueChanged[int].connect(self.update_npts)
        self.label['npts'].editingFinished.connect(self.update_box_npts)
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
        Set min, max, default and link to label
        :param slider: All existing slider with key from keylist.
        :type slider: dict
        :param label: All existing label wiht key from keylist.
        :type label: dict
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
