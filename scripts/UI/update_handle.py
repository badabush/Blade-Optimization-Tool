import math

class UpdateHandler:
    """
    A very quick and dirty approach... Alternatively, creating a custom DoubleSlider class would be way cleaner.
    TODO: fix this when bored.
    """

    def update_box_alpha1(self):
        value = self.label['alpha1'].value()
        self.slider['alpha1'].setSliderPosition(value)

    def update_box_alpha2(self):
        value = self.label['alpha2'].value()
        self.slider['alpha2'].setSliderPosition(value)

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

    def update_th(self, value):
        self.label['th'].setValue(float(value) / self.scale)

    def update_box_th(self):
        value = self.label['th'].value() * self.scale
        self.slider['th'].setSliderPosition(value)

    def update_xmax_th(self, value):
        self.label['xmax_th'].setValue(float(value) / self.scale)

    def update_box_xmax_th(self):
        value = self.label['xmax_th'].value() * self.scale
        self.slider['xmax_th'].setSliderPosition(value)

    def update_xmax_camber(self, value):
        self.label['xmax_camber'].setValue(float(value) / self.scale)

    def update_box_xmax_camber(self):
        value = self.label['xmax_camber'].value() * self.scale
        self.slider['xmax_camber'].setSliderPosition(value)

    def update_thle(self, value):
        if (float(value) / self.scale) < 0.005 and (float(value) / self.scale) > 0.0:
            self.label['th_le'].setValue(0.005)
        else:
            self.label['th_le'].setValue(float(value) / self.scale)

    def update_box_thle(self):
        value = self.label['th_le'].value()  # * self.scale
        if value < 0.01 and value > 0.0:
            value = 0.01 * self.scale
        self.slider['th_le'].setSliderPosition(value)

    def update_thte(self, value):
        if (float(value) / self.scale) < 0.005 and (float(value) / self.scale) > 0.0:
            self.label['th_te'].setValue(0.005)
        else:
            self.label['th_te'].setValue(float(value) / self.scale)

    def update_box_thte(self):
        value = self.label['th_te'].value()  # * self.scale
        if value < 0.005 and value > 0.0:
            value = 0.005 * self.scale
        self.slider['th_te'].setSliderPosition(value)

    def update_dist_blades(self, value):
        self.label['dist_blades'].setValue(float(value) / self.scale)

    def update_box_dist_blades(self):
        value = self.label['dist_blades'].value() * self.scale
        self.slider['dist_blades'].setSliderPosition(value)

    def update_radio_blades(self):
        # get radio state
        if self.radio_blade1.isChecked():
            self.select_blade = 1
            self.ds_blade2 = self.get_labelval()
            self.set_labelval(self.ds_blade1)

        elif self.radio_blade2.isChecked():
            self.select_blade = 2
            self.ds_blade1 = self.get_labelval()
            self.set_labelval(self.ds_blade2)
        print(self.select_blade)

    def get_labelval(self):
        # get values
        ds = {}
        for key in self.param_keys:
            ds[key] = self.label[key].value()
        return ds

    def set_labelval(self, ds):
        self.label['alpha1'].setValue(ds['alpha1'])
        self.slider['alpha1'].setSliderPosition(ds['alpha1'])
        self.label['alpha2'].setValue(ds['alpha2'])
        self.slider['alpha2'].setSliderPosition(ds['alpha2'])
        self.label['lambd'].setValue(ds['lambd'])
        self.slider['lambd'].setSliderPosition(ds['lambd'])
        self.label['th'].setValue(ds['th'])
        self.slider['th'].setSliderPosition(ds['th'] * self.scale)
        self.label['xmax_th'].setValue(ds['xmax_th'])
        self.slider['xmax_th'].setSliderPosition(ds['xmax_th'] * self.scale)
        self.label['xmax_camber'].setValue(ds['xmax_camber'])
        self.slider['xmax_camber'].setSliderPosition(ds['xmax_camber'] * self.scale)
        self.label['th_le'].setValue(ds['th_le'])
        self.slider['th_le'].setSliderPosition(ds['th_le'] * self.scale)
        self.label['th_te'].setValue(ds['th_te'])
        self.slider['th_te'].setSliderPosition(ds['th_te'] * self.scale)

    def update_inputs(self):
        # get values
        ds = {}
        for key in self.param_keys:
            ds[key] = self.label[key].value()

        # get values from menu items
        ds['thdist_ver'] = self.thdist_ver
        ds['nblades'] = self.nblades
        ds['pts'] = self.points
        ds['selected_blade'] = 0
        self.ds = ds
        self.ds1 = ds
        self.ds2 = ds
        self.m.plot(self.ds,ds1=self.ds1,ds2=self.ds2)
        print('Updating Plot')

    def update_select(self):
        # get values
        if self.select_blade == 1:
            self.ds['selected_blade'] = 1
            
            ds1 = {}
            for key in self.param_keys:
                ds1[key] = self.label[key].value()
    
            # get values from menu items
            ds1['thdist_ver'] = self.thdist_ver
            ds1['nblades'] = self.nblades
            ds1['pts'] = self.points
            self.ds1 = ds1
            self.m.plot(self.ds, ds1=self.ds1, ds2=self.ds2)
        elif self.select_blade == 2:
            self.ds['selected_blade'] = 2

            ds2 = {}
            for key in self.param_keys:
                ds2[key] = self.label[key].value()

            # get values from menu items
            ds2['thdist_ver'] = self.thdist_ver
            ds2['nblades'] = self.nblades
            ds2['pts'] = self.points
            self.ds2 = ds2
            self.m.plot(self.ds, ds1=self.ds1, ds2=self.ds2)

    def set_default(self):
        # set values
        for key in self.param_keys:
            self.label[key].setValue(self.restraints[key][3])
            if key == 'npts':
                self.slider[key].setSliderPosition(self.restraints[key][3] / 100)
            elif self.restraints[key][1] > 1:
                self.slider[key].setSliderPosition(self.restraints[key][3])
            else:
                self.slider[key].setSliderPosition(self.restraints[key][3] * self.scale)
        print('Resetting Values')

    def update_thdist_V1(self):
        self.thdist_ver = 0

    def update_thdist_V2(self):
        self.thdist_ver = 1

    def update_nblades_single(self):
        self.nblades = 'single'
        self.radio_blade1.setHidden(True)
        self.radio_blade2.setHidden(True)
        self.btn_update_sel.setHidden(True)

    def update_nblades_tandem(self):
        self.ds_blade1 = self.get_labelval()
        self.ds_blade2 = self.get_labelval()
        self.nblades = 'tandem'
        self.radio_blade1.setVisible(True)
        self.radio_blade2.setVisible(True)
        self.radio_blade1.setChecked(True)

        self.btn_update_sel.setVisible(True)
