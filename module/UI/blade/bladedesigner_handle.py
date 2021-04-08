import math
import pandas as pd
from blade.bladetools import initialize_blade_df


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
        value = self.label['lambd'].value() * 10
        self.slider['lambd'].setSliderPosition(value)

    def update_lambd(self, value):
        """
        Set Label to input value wiht scale for lambda (lambd).
        """
        self.label['lambd'].setValue(float(value) / 10)

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

    def update_gamma_te(self, value):
        """
        Set Label to input value with scale for gamma trailing edge (gamma_te).
        :param value: input value
        :type value: float
        """
        self.label['gamma_te'].setValue(float(value) / self.scale)

    def update_box_gamma_te(self):
        """
        Scale Value from Label, set Slider Position of gamma trailing edge (gamma_te).
        """
        value = self.label['gamma_te'].value() * self.scale
        self.slider['gamma_te'].setSliderPosition(value)

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

    def update_PP(self, value):
        """
        TODO:FILL
        :param value: input value
        :type value: float
        """
        self.label['PP'].setValue(float(value) / self.scale)

    def update_box_PP(self):
        """
        Scale Value from Label, set Slider Position of thickness (th).
        """
        value = self.label['PP'].value() * self.scale
        self.slider['PP'].setSliderPosition(value)

    def update_AO(self, value):
        """
        TODO:FILL
        :param value: input value
        :type value: float
        """
        self.label['AO'].setValue(float(value) / self.scale)

    def update_box_AO(self):
        """
        Scale Value from Label, set Slider Position of thickness (th).
        """
        value = self.label['AO'].value() * self.scale
        self.slider['AO'].setSliderPosition(value)

    def update_chord_dist(self, value):
        """
        TODO:FILL
        :param value: input value
        :type value: float
        """
        self.label['chord_dist'].setValue(float(value) / self.scale)

    def update_box_chord_dist(self):
        """
        Scale Value from Label, set Slider Position of thickness (th).
        """
        value = self.label['chord_dist'].value() * self.scale
        self.slider['chord_dist'].setSliderPosition(value)

    def update_radio_blades(self):
        """
        Radio Buttons for Tandem Blades (switch between blade 1 and 2). Make xy position control for 2nd blade visible
        if 2nd blade is selected. Save values from slider/labels as soon as the other radio button is checked.
        """
        # get radio state
        if self.radio_blade1.isChecked():
            self.select_blade = 1
            ds2 = self.get_labelval()
            for key in ds2.keys():
                self.ds2[key] = ds2[key]
            if not self.ds1['chord_dist'] == (1 - self.ds2['chord_dist']):
                self.ds1['chord_dist'] = 1 - self.ds2['chord_dist']
            self.set_labelval(self.ds1)

        elif self.radio_blade2.isChecked():
            self.select_blade = 2
            ds1 = self.get_labelval()
            for key in ds1.keys():
                self.ds1[key] = ds1[key]
            try:
                if not self.ds2['chord_dist'] == (1 - self.ds1['chord_dist']):
                    self.ds2['chord_dist'] = 1 - self.ds1['chord_dist']

                self.set_labelval(self.ds2)
            except AttributeError:
                self.set_labelval(self.ds1)
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
        self.slider['lambd'].setSliderPosition(ds['lambd'] * 10)
        self.label['th'].setValue(ds['th'])
        self.slider['th'].setSliderPosition(ds['th'] * self.scale)
        self.label['xmax_th'].setValue(ds['xmax_th'])
        self.slider['xmax_th'].setSliderPosition(ds['xmax_th'] * self.scale)
        self.label['xmax_camber'].setValue(ds['xmax_camber'])
        self.slider['xmax_camber'].setSliderPosition(ds['xmax_camber'] * self.scale)
        self.label['gamma_te'].setValue(ds['gamma_te'])
        self.slider['gamma_te'].setSliderPosition(ds['gamma_te'] * self.scale)
        self.label['th_le'].setValue(ds['th_le'])
        self.slider['th_le'].setSliderPosition(ds['th_le'] * self.scale)
        self.label['th_te'].setValue(ds['th_te'])
        self.slider['th_te'].setSliderPosition(ds['th_te'] * self.scale)

        self.label['dist_blades'].setValue(ds['dist_blades'])
        self.slider['dist_blades'].setSliderPosition(ds['dist_blades'] * self.scale)
        self.label['PP'].setValue(ds['PP'])
        self.slider['PP'].setSliderPosition(ds['PP'] * self.scale)
        self.label['AO'].setValue(ds['AO'])
        self.slider['AO'].setSliderPosition(ds['AO'] * self.scale)
        self.label['chord_dist'].setValue(ds['chord_dist'])
        self.slider['chord_dist'].setSliderPosition(ds['chord_dist'] * self.scale)

    def update_all(self):
        """
        If Button: [Update All] is clicked, get values from labels and plot.
        """
        # get values
        # ds = {}
        ds = initialize_blade_df()
        for key in self.param_keys:
            ds[key] = self.label[key].value()

        ds["th_dist_ver"] = self.thdist_ver
        ds['nblades'] = self.nblades
        ds['spline_pts'] = self.camber_spline_pts
        ds['thdist_pts'] = self.thdist_spline_pts
        ds['blade'] = "both"
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
                    {'x': self.imported_blade.x, 'y': self.imported_blade.y, 'x_offset': self.in_blade_offset[0],
                     'y_offset': self.in_blade_offset[1]})
            else:
                self.ds_import = 0
        except AttributeError as e:
            print(e)
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
                    {'x1': self.imported_blade1.x, 'y1': self.imported_blade1.y,
                     'x2': self.imported_blade2.x, 'y2': self.imported_blade2.y,
                     'x_offset': self.in_blade_offset[0], 'y_offset': self.in_blade_offset[1]})
            else:
                self.ds_import = 0
        except AttributeError as e:
            self.ds_import = 0

        if self.select_blade == 1:

            self.ds['blade'] = "front"
            ds1 = {}
            for key in self.param_keys:
                ds1[key] = self.label[key].value()
            # get values from menu items
            ds1['th_dist_ver'] = self.thdist_ver
            ds1['blade'] = self.ds["blade"]
            # ds1['chord_dist'] = 0.5 #fixme
            ds1['nblades'] = self.nblades
            ds1['spline_pts'] = self.camber_spline_pts
            ds1['thdist_pts'] = self.thdist_spline_pts
            ds1['npts'] = self.number_of_points
            ds1['l_chord'] = self.length_chord
            ds1['x_offset'] = ds1['AO'] * ds1['dist_blades']  # AO
            ds1['y_offset'] = (1 - ds1['PP']) * ds1['dist_blades']  # PP

            self.ds2['x_offset'] = ds1['AO'] * ds1['dist_blades']  # AO
            self.ds2['y_offset'] = (1 - ds1['PP']) * ds1['dist_blades']  # PP
            # invert value from ds1
            self.ds2['chord_dist'] = 1 - ds1["chord_dist"]  # chord dist
            # make sure ds1 and ds2 have the same values for ao,pp,div
            self.ds2['dist_blades'] = ds1["dist_blades"]
            self.ds2['PP'] = ds1["PP"]
            self.ds2['AO'] = ds1["AO"]
            self.ds1 = ds1

            self.m.plot(self.ds, ds1=self.ds1, ds2=self.ds2, ds_import=self.ds_import)

        elif self.select_blade == 2:

            self.ds['blade'] = "aft"
            ds2 = {}
            for key in self.param_keys:
                ds2[key] = self.label[key].value()
            # get values from menu items
            ds2['th_dist_ver'] = self.thdist_ver
            ds2['blade'] = self.ds["blade"]
            # ds2['chord_dist'] = ds2
            ds2['nblades'] = self.nblades
            ds2['spline_pts'] = self.camber_spline_pts
            ds2['thdist_pts'] = self.thdist_spline_pts
            ds2['npts'] = self.number_of_points
            ds2['l_chord'] = self.length_chord
            # same xy offset as in ds1, but required here to update div,PP,AO when blade 2 is selected
            ds2['x_offset'] = ds2['AO'] * ds2['dist_blades']  # AO
            ds2['y_offset'] = (1 - ds2['PP']) * ds2['dist_blades']  # PP

            self.ds1['x_offset'] = ds2['AO'] * ds2['dist_blades']  # AO
            self.ds1['y_offset'] = (1 - ds2['PP']) * ds2['dist_blades']  # PP
            # self.ds1['chord_dist'] = 1 - ds2["chord_dist"]  # chord dist
            self.ds1['chord_dist'] = 1 - ds2["chord_dist"]  # chord dist
            # make sure ds1 and ds2 have the same values for ao,pp,div
            self.ds1['dist_blades'] = ds2["dist_blades"]
            self.ds1['PP'] = ds2["PP"]
            self.ds1['AO'] = ds2["AO"]
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
        self.btn_update_sel.setEnabled(False)
        self.btn_update_all.setEnabled(True)

    def update_nblades_tandem(self):
        """
        Menu option for tandem blades. Show Tandem Radio buttons and [update select] button as well as the blade 2
        position controls.
        """
        ds1 = self.get_labelval()
        ds2 = self.get_labelval()
        for key in ds1.keys():
            self.ds1[key] = ds1[key]
            self.ds2[key] = ds2[key]

        self.nblades = 'tandem'
        self.radio_blade1.setVisible(True)
        self.radio_blade2.setVisible(True)
        self.radio_blade1.setChecked(True)

        self.btn_update_sel.setEnabled(True)
        self.btn_update_all.setEnabled(False)
        self.update_all()
        self.update_select()
        self.select_blade = 2
        self.update_select()
        self.select_blade = 1

    def update_in_up(self):
        """
        Imported Blade position control, button [up].
        """
        self.ds_import['y_offset'] += 0.001
        self.in_blade_offset[1] = self.ds_import['y_offset']
        self.m.plot(self.ds, ds1=self.ds1, ds2=self.ds2, ds_import=self.ds_import)

    def update_in_down(self):
        """
        Imported Blade position control, button [down].
        """
        self.ds_import['y_offset'] -= 0.001
        self.in_blade_offset[1] = self.ds_import['y_offset']
        self.m.plot(self.ds, ds1=self.ds1, ds2=self.ds2, ds_import=self.ds_import)

    def update_in_left(self):
        """
        Imported Blade position control, button [left].
        """
        self.ds_import['x_offset'] -= 0.001
        self.in_blade_offset[0] = self.ds_import['x_offset']
        self.m.plot(self.ds, ds1=self.ds1, ds2=self.ds2, ds_import=self.ds_import)

    def update_in_right(self):
        """
        Imported Blade position control, button [right].
        """
        self.ds_import['x_offset'] += 0.001
        self.in_blade_offset[0] = self.ds_import['x_offset']
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
