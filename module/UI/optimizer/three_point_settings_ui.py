import configparser

from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore


class ThreePointSettingsUI(QtWidgets.QDialog):

    def __init__(self, ):
        super(ThreePointSettingsUI, self).__init__()
        uic.loadUi('UI/qtdesigner/threepointsettingswindow.ui', self)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.paths = {}
        # link buttons
        self.btn_apply.clicked.connect(self._apply)
        self.btn_cls.clicked.connect(self._close)

        # set default values from config
        self.configfile = "config/three_point_paths.ini"
        self.config = configparser.ConfigParser()
        self.config.read(self.configfile)
        self.set_paths()


    def set_paths(self):
        # get from config
        self.paths['design'] = self.config['paths']['design']
        self.paths['lower'] = self.config['paths']['lower']
        self.paths['upper'] = self.config['paths']['upper']

        # set boxes
        self.box_path_design.setText(self.paths['design'])
        self.box_path_lower.setText(self.paths['lower'])
        self.box_path_upper.setText(self.paths['upper'])

    def get_input(self):
        # get paths from boxes
        self.paths['design'] = self.box_path_design.text()
        self.paths['lower'] = self.box_path_lower.text()
        self.paths['upper'] = self.box_path_upper.text()

    def save_config(self):
        """
        Saves the most recent user input to config. Automatically called when APPLY is pressed.
        :return:
        """
        cfgfile = open(self.configfile, 'w')
        # config_checkboxes = self.config["checkboxes"]
        for key, val in self.paths.items():
                self.config.set("paths", key, str(val))
        self.config.write(cfgfile)
        cfgfile.close()

    def _close(self):
        self.close()

    def _apply(self):
        """
        If apply button is clicked, update checkbox dict and value variables.
        :return:
        """
        self.get_input()
        self.save_config()
        self._close()
