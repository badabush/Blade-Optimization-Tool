from module.optimizer.ssh_login import ssh_connect
class OptimHandler:
    """
    Contains update GUI elements for the Optimizer Tab.
    """

    def optim_handler_init(self):
        """
        Initialize optimizer tab gui elements e.g. link buttons
        """
        self.btn_testconnect.clicked.connect(self.ssh_connect)
        self.btn_topcmd.clicked.connect(self.display_top)


    def ssh_connect(self):
        self.sshobj = ssh_connect.Ssh_Util()
        if self.sshobj.failure:
            self.outputbox("No config.ini file found. Setup credentials first!")
            return
        self.sshobj.connect()

    def display_top(self):
        try:
            if not self.sshobj:
                self.ssh_connect()
        except AttributeError as e:
            self.ssh_connect()
            self.outputbox("Connecting...")
            top_usage = self.sshobj.send_cmd("top -b -n 1")
            self.outputbox(top_usage)

