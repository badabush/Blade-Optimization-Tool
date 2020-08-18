from PyQt5.QtWidgets import QSizePolicy
from PyQt5 import QtWidgets, uic

class PuttyLoginUi(QtWidgets.QMainWindow):

    def __init__(self):
        super(PuttyLoginUi, self).__init__()
        uic.loadUi('UI/qtdesigner/loginwindow.ui', self)
        self.btn_cls.clicked.connect(self.close_window)
        self.btn_login.clicked.connect(self.connect)
        # Connect Buttons to updating plot.
        # self.p1_down.clicked.connect(self.update_p1_down)

    def connect(self):
        username = self.input_usr.text()
        password = self.input_pwd.text()

        if (not self.input_usr) or (not self.input_pwd):
            return

    def close_window(self):
        """
        Close Window on button clicked.
        """
        self.close()