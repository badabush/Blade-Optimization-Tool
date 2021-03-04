import configparser

from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore


class DeapConfigUi(QtWidgets.QDialog):

    def __init__(self, ):
        super(DeapConfigUi, self).__init__()
        uic.loadUi('UI/qtdesigner/deapwindow.ui', self)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        # link buttons
        self.btn_apply.clicked.connect(self._apply)
        self.btn_cls.clicked.connect(self._close)
        self.deap_config_cb = {
            "pp": self.cb_pp,
            "ao": self.cb_ao,
            "div": self.cb_division,
            "alph11": self.cb_alpha11,
            "alph12": self.cb_alpha12,
            "alph21": self.cb_alpha21,
            "alph22": self.cb_alpha22,
            "lambd1": self.cb_lambd1,
            "lambd2": self.cb_lambd2,
            "th1": self.cb_th1,
            "th2": self.cb_th2,
            "xmaxth1": self.cb_xmaxth1,
            "xmaxth2": self.cb_xmaxth2,
            "xmaxcamber1": self.cb_xmaxcamber1,
            "xmaxcamber2": self.cb_xmaxcamber2,
            "gamma_te1": self.cb_gamma_te1,
            "gamma_te2": self.cb_gamma_te2,
            "leth1": self.cb_leth1,
            "leth2": self.cb_leth2,
            "teth1": self.cb_teth1,
            "teth2": self.cb_teth2
        }

        self.deap_config_inputs = {
            "pop_size": self.input_pop,
            "max_gens": self.input_gen,
            "cxpb": self.input_cxpb,
            "mutpb": self.input_mutpb,
            "penalty_factor": self.input_penalty_factor,
            "random_seed": self.input_rnd_seed
        }

        self.cblist = {}
        self.vallist = {}

        # set default values from config
        self.configfile = "config/deap_settings.ini"
        self.config = configparser.ConfigParser()
        self.config.read(self.configfile)
        self.set_default()

        # get checkboxes on GUI start (fill dict with default values)
        self.get_checkbox()
        # get initial values on GUI start
        self.get_values()

    def get_checkbox(self):
        """
        Get checkbox states and write them into dict.
        :return:
        """
        for key, widget in self.deap_config_cb.items():
            if widget.isChecked() == True:
                self.cblist[key] = 1
                # config_checkboxes = self.config["checkboxes"]
            else:
                self.cblist[key] = 0

    def get_values(self):
        """
        Get Values (not CB) from Input boxes.
        :return:
        """
        self.vallist['pop_size'] = self.input_pop.value()
        self.vallist['max_gens'] = self.input_gen.value()
        self.vallist['cxpb'] = self.input_cxpb.value()
        self.vallist['mutpb'] = self.input_mutpb.value()
        self.vallist['penalty_factor'] = self.input_penalty_factor.value()
        self.vallist['random_seed'] = self.input_rnd_seed.value()
        self.vallist['objective_params'] = [self.input_obj_param_A.value(), self.input_obj_param_B.value(),
                                            self.input_obj_param_C.value()]

    def _close(self):
        self.close()

    def set_default(self):
        for section in self.config.sections():
            for option in self.config.options(section):
                if section == "checkboxes":
                    state = self.config.getboolean(section, option)
                    self.deap_config_cb[option].setChecked(state)
                elif section == "DEAP":
                    self.deap_config_inputs[option].setValue(self.config.getfloat(section, option))

    def save_config(self):
        """
        Saves the most recent user input to config. Automatically called when APPLY is pressed.
        :return:
        """
        cfgfile = open(self.configfile, 'w')
        # config_checkboxes = self.config["checkboxes"]
        for key, state in self.cblist.items():
            if state:
                self.config.set("checkboxes", key, 'true')
            else:
                self.config.set("checkboxes", key, 'false')

        for key, val in self.vallist.items():
            self.config.set("DEAP", key, str(val))
        self.config.write(cfgfile)
        cfgfile.close()

    def _apply(self):
        """
        If apply button is clicked, update checkbox dict and value variables.
        :return:
        """
        self.get_checkbox()
        self.get_values()
        self.save_config()
        self._close()
