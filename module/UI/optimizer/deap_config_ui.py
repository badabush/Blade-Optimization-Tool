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
            "alph1": self.cb_alpha1,
            "alph2": self.cb_alpha2,
            "lambd": self.cb_lambda,
            "th": self.cb_th,
            "xmaxth": self.cb_xmaxth,
            "xmaxcamber": self.cb_xmaxcmb,
            "leth": self.cb_leth,
            "teth": self.cb_teth}

        self.deap_config_inputs = {
            "pop_size": self.input_pop,
            "max_gens": self.input_gen,
            "cxpb": self.input_cxpb,
            "mutpb": self.input_mutpb

        }
        self.cblist = {}
        self.vallist = {}

        # set default values from config
        self.configfile = "config/deap_default_settings.ini"
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
                config_checkboxes = self.config["checkboxes"]
            else:
                self.cblist[key] = 0

    def get_values(self):
        """
        Get Values from Input boxes.
        :return:
        """
        self.vallist['pop_size'] = self.input_pop.value()
        self.vallist['max_gens'] = self.input_gen.value()
        self.vallist['cxpb'] = self.input_cxpb.value()
        self.vallist['mutpb'] = self.input_mutpb.value()

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
        Saves the most recent user input to config. Automatically called when APPLY is presed.
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
