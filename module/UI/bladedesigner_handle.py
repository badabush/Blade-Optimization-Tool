import math
import pandas as pd


class BDUpdateHandler:
    """
    Contains update GUI elements for the BladeDesign Tab.

    A very quick and dirty approach... Alternatively, creating a custom DoubleSlider class would be way cleaner.
    TODO: fix this when bored.
    """

    def update_box_alpha1(self):
        """
        Get Value from Slider, apply to Label (alpha1).
        """
        value = self.label['alpha1'].value()
        self.slider['alpha1'].setSliderPosition(value)

    def update_box_alpha2(self):
        """
        Get Value from Slider, apply to Label (alpha2).
        """
        value = self.label['alpha2'].value()
        self.slider['alpha2'].setSliderPosition(value)

    def update_box_lambd(self):
        """
        Get Value from Slider, apply to Label Lambda (lambd).
        """
        value = self.label['lambd'].value()
        self.slider['lambd'].setSliderPosition(value)

    def update_box_npts(self):
        """
        Set Value for Label and Slider Position for Number of Points (npts) with custom scale (100) **obsolete**.
        """
        val_raw = self.label['npts'].value()
        if (val_raw % 100) > 50:
            value = math.ceil(val_raw / 100)
        else:
            value = math.floor(val_raw / 100)
        self.label['npts'].setValue(float(value) * 100)
        self.slider['npts'].setSliderPosition(value)

    def update_th(self, value):
        """
        Set Label to input value with scale for thickness (th).
        :param value: input value
        :type value: float
        """
        self.label['th'].setValue(float(value) / self.scale)

    def update_box_th(self):
        """
        Scale Value from Label, set Slider Position of thickness (th).
        """
        value = self.label['th'].value() * self.scale
        self.slider['th'].setSliderPosition(value)

    def update_xmax_th(self, value):
        """
        Set Label to input value with scale for maximum thickness x-coordinate (xmax_th).
        :param value: input value
        :type value: float
        """
        self.label['xmax_th'].setValue(float(value) / self.scale)

    def update_box_xmax_th(self):
        """
        Scale Value from Label, set Slider Position of thickness (th).
        """
        value = self.label['xmax_th'].value() * self.scale
        self.slider['xmax_th'].setSliderPosition(value)

    def update_xmax_camber(self, value):
        """
        Set Label to input value with scale for maximum camber position (xmax_camber).
        :param value: input value
        :type value: float
        """
        self.label['xmax_camber'].setValue(float(value) / self.scale)

    def update_box_xmax_camber(self):
        """
        Scale Value from Label, set Slider Position of maximum camber position (xmax_camber).
        """
        value = self.label['xmax_camber'].value() * self.scale
        self.slider['xmax_camber'].setSliderPosition(value)

    def update_thle(self, value):
        """
        Set Label to input value with scale and excluded range for thickness LE (thle).
        :param value: input value
        :type value: float
        """
        if (float(value) / self.scale) < 0.005 and (float(value) / self.scale) > 0.0:
            self.label['th_le'].setValue(0.005)
        else:
            self.label['th_le'].setValue(float(value) / self.scale)

    def update_box_thle(self):
        """
        Scale Value and exclude range from Label, set Slider Position of thickness LE (thle).
        """
        value = self.label['th_le'].value()  # * self.scale
        if value < 0.01 and value > 0.0:
            value = 0.01 * self.scale
        self.slider['th_le'].setSliderPosition(value)

    def update_thte(self, value):
        """
        Set Label to input value with scale and excluded range for thickness TE (thle).
        :param value: input value
        :type value: float
        """
        if (float(value) / self.scale) < 0.005 and (float(value) / self.scale) > 0.0:
            self.label['th_te'].setValue(0.005)
        else:
            self.label['th_te'].setValue(float(value) / self.scale)

    def update_box_thte(self):
        """
        Scale Value and exclude range from Label, set Slider Position of thickness TE (thte).
        """
        value = self.label['th_te'].value()  # * self.scale
        if value < 0.005 and value > 0.0:
            value = 0.005 * self.scale
        self.slider['th_te'].setSliderPosition(value)

    def update_dist_blades(self, value):
        """
        Set Label to input value with scale for y-distance between blades (the one above the single/tandem) (dist_blades)
        :param value: input value
        :type value: float
        """
        self.label['dist_blades'].setValue(float(value) / self.scale)

    def update_box_dist_blades(self):
        """
        Scale Value from Label, set Slider Position of thickness (th).
        """
        value = self.label['dist_blades'].value() * self.scale
        self.slider['dist_blades'].setSliderPosition(value)

    def update_radio_blades(self):
        """
        Radio Buttons for Tandem Blades (switch between blade 1 and 2). Make xy position control for 2nd blade visible
        if 2nd blade is selected. Save values from slider/labels as soon as the other radio button is checked.
        """
        # get radio state
        if self.radio_blade1.isChecked():
            self.update_b2_control_vis(0)
            self.select_blade = 1
            self.ds_blade2 = self.get_labelval()
            self.set_labelval(self.ds_blade1)

        elif self.radio_blade2.isChecked():
            self.update_b2_control_vis(1)
            self.select_blade = 2
            self.ds_blade1 = self.get_labelval()
            self.set_labelval(self.ds_blade2)
        print(self.select_blade)

    def get_labelval(self):
        """
        Get values and save to dataset (radio button checked). Returns the dataset.

        :return: ds
        :rtype ds: dict
        """
        # get values
        ds = {}
        for key in self.param_keys:
            ds[key] = self.label[key].value()
        return ds

    def set_labelval(self, ds):
        """
        Get values from saved state and update slider position and labels (radio button checked).

        :param ds: dataset from saved radio button
        :type ds: dict
        """

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

    def update_all(self):
        """
        If Button: [Update All] is clicked, get values from labels and plot.
        """
        # get values
        ds = {}
        for key in self.param_keys:
            ds[key] = self.label[key].value()

        # get values from menu items
        ds['thdist_ver'] = self.thdist_ver
        ds['nblades'] = self.nblades
        ds['pts'] = self.camber_spline_pts
        ds['pts_th'] = self.thdist_spline_pts
        ds['selected_blade'] = 0
        ds['npts'] = self.number_of_points
        ds['l_chord'] = self.length_chord
        self.ds = ds

        self.ds1 = self.ds
        self.ds2 = self.ds
        self.ds2['x_offset'] = self.blade2_offset[0]
        self.ds2['y_offset'] = self.blade2_offset[1]

        try:
            # try to get data from imported blade
            if self.imported_blade_vis == 1:
                self.ds_import = pd.DataFrame(
                    {'x': self.imported_blade.x, 'y': self.imported_blade.y, 'x_offset': 0, 'y_offset': 0})
            else:
                self.ds_import = 0
        except AttributeError as e:
            self.ds_import = 0
        self.m.plot(self.ds, ds1=self.ds1, ds2=self.ds2, ds_import=self.ds_import)
        print('Updating Plot')

    def update_select(self):
        """
        If Button: [Update Select] is clicked, get values from labels and plot selected blade from radio buttons.
        """
        # get values
        try:
            if self.imported_blade_vis == 1:
                self.ds_import = pd.DataFrame(
                    {'x': self.imported_blade.x, 'y': self.imported_blade.y, 'x_offset': 0, 'y_offset': 0})
            else:
                self.ds_import = 0
        except AttributeError as e:
            self.ds_import = 0

        if self.select_blade == 1:

            self.ds['selected_blade'] = 1
            ds1 = {}
            for key in self.param_keys:
                ds1[key] = self.label[key].value()
            # get values from menu items
            ds1['thdist_ver'] = self.thdist_ver
            ds1['nblades'] = self.nblades
            ds1['pts'] = self.camber_spline_pts
            ds1['pts_th'] = self.thdist_spline_pts
            ds1['npts'] = self.number_of_points
            ds1['l_chord'] = self.length_chord
            self.ds1 = ds1
            self.m.plot(self.ds, ds1=self.ds1, ds2=self.ds2, ds_import=self.ds_import)

        elif self.select_blade == 2:

            self.ds['selected_blade'] = 2
            ds2 = {}
            for key in self.param_keys:
                ds2[key] = self.label[key].value()
            # get values from menu items
            ds2['thdist_ver'] = self.thdist_ver
            ds2['nblades'] = self.nblades
            ds2['pts'] = self.camber_spline_pts
            ds2['pts_th'] = self.thdist_spline_pts
            ds2['npts'] = self.number_of_points
            ds2['l_chord'] = self.length_chord
            ds2['x_offset'] = self.blade2_offset[0]
            ds2['y_offset'] = self.blade2_offset[1]
            self.ds2 = ds2
            self.m.plot(self.ds, ds1=self.ds1, ds2=self.ds2, ds_import=self.ds_import)

    def set_default(self):
        """
        If Button: [default] is clicked, set all visible slider positions and label to default position defined in
        restraints.txt.
        """
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
        """
        Menu option Thickness distribution V1 is selected.
        """
        self.thdist_ver = 0

    def update_thdist_V2(self):
        """
        Menu option Thickness distribution V2 is selected (default).
        """
        self.thdist_ver = 1

    def update_nblades_single(self):
        """
        Menu option for single blades. Hide Tandem Radio buttons and [update select] button as well as the blade 2
        position controls.
        """
        self.nblades = 'single'
        self.radio_blade1.setHidden(True)
        self.radio_blade2.setHidden(True)
        self.btn_update_sel.setHidden(True)
        self.update_b2_control_vis(0)

    def update_nblades_tandem(self):
        """
        Menu option for tandem blades. Show Tandem Radio buttons and [update select] button as well as the blade 2
        position controls.
        """
        self.ds_blade1 = self.get_labelval()
        self.ds_blade2 = self.get_labelval()
        self.nblades = 'tandem'
        self.radio_blade1.setVisible(True)
        self.radio_blade2.setVisible(True)
        self.radio_blade1.setChecked(True)

        self.btn_update_sel.setVisible(True)
        # self.m.plot(self.ds, ds1=self.ds1, ds2=self.ds2)

    def update_B2_up(self):
        """
        Blade 2 position control, button [up].
        """
        self.blade2_offset[1] += 0.01
        self.ds2['y_offset'] = self.blade2_offset[1]
        self.m.plot(self.ds, ds1=self.ds1, ds2=self.ds2)

    def update_B2_down(self):
        """
        Blade 2 position control, button [down].
        """
        self.blade2_offset[1] -= 0.01
        self.ds2['y_offset'] = self.blade2_offset[1]
        self.m.plot(self.ds, ds1=self.ds1, ds2=self.ds2)

    def update_B2_left(self):
        """
        Blade 2 position control, button [left].
        """
        self.blade2_offset[0] -= 0.01
        self.ds2['x_offset'] = self.blade2_offset[0]
        self.m.plot(self.ds, ds1=self.ds1, ds2=self.ds2)

    def update_B2_right(self):
        """
        Blade 2 position control, button [right].
        """
        self.blade2_offset[0] += 0.01
        self.ds2['x_offset'] = self.blade2_offset[0]
        self.m.plot(self.ds, ds1=self.ds1, ds2=self.ds2)

    def update_in_up(self):
        """
        Imported Blade position control, button [up].
        """
        self.ds_import['y_offset'] += 0.001
        self.m.plot(self.ds, ds1=self.ds1, ds2=self.ds2, ds_import=self.ds_import)

    def update_in_down(self):
        """
        Imported Blade position control, button [down].
        """
        self.ds_import['y_offset'] -= 0.001
        self.m.plot(self.ds, ds1=self.ds1, ds2=self.ds2, ds_import=self.ds_import)

    def update_in_left(self):
        """
        Imported Blade position control, button [left].
        """
        self.ds_import['x_offset'] -= 0.001
        self.m.plot(self.ds, ds1=self.ds1, ds2=self.ds2, ds_import=self.ds_import)

    def update_in_right(self):
        """
        Imported Blade position control, button [right].
        """
        self.ds_import['x_offset'] += 0.001
        self.m.plot(self.ds, ds1=self.ds1, ds2=self.ds2, ds_import=self.ds_import)

    def update_imported_blade(self):
        """
        Show/Hide imported blade in plot.
        """
        if self.imported_blade_vis == 1:
            self.update_in_control_vis(0)
            self.imported_blade_vis = 0
        else:
            self.update_in_control_vis(1)
            self.imported_blade_vis = 1

    def update_b2_control_vis(self, visible=0):
        """
        Control for 2nd blade position. Hide at GUI start.
        """

        if visible == 0:
            self.label_pos_b2.setHidden(True)
            self.btn_b2_up.setHidden(True)
            self.btn_b2_down.setHidden(True)
            self.btn_b2_left.setHidden(True)
            self.btn_b2_right.setHidden(True)
        else:
            self.label_pos_b2.setVisible(True)
            self.btn_b2_up.setVisible(True)
            self.btn_b2_down.setVisible(True)
            self.btn_b2_left.setVisible(True)
            self.btn_b2_right.setVisible(True)

    def update_in_control_vis(self, visible=0):
        """
        Control for 2nd blade position. Hide at GUI start.
        """

        if visible == 0:
            self.label_pos_in.setHidden(True)
            self.btn_in_up.setHidden(True)
            self.btn_in_down.setHidden(True)
            self.btn_in_left.setHidden(True)
            self.btn_in_right.setHidden(True)
        else:
            self.label_pos_in.setVisible(True)
            self.btn_in_up.setVisible(True)
            self.btn_in_down.setVisible(True)
            self.btn_in_left.setVisible(True)
            self.btn_in_right.setVisible(True)
