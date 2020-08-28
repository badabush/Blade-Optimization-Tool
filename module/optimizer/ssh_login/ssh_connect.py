import paramiko
import os, sys
import json
from pathlib import Path
# import socket

from jumpssh import SSHSession


class Ssh_Util:
    "Class to connect to remote server"

    def __init__(self):
        self.read_config()
        self.conf_ssh = self.conf_file["ssh"]
        self.ssh_output = None
        self.ssh_error = None
        self.client = None

        self.host = self.conf_ssh["host"]
        self.username = self.conf_ssh["user"]
        self.password = self.conf_ssh["passwd"]
        # self.username = username
        # self.password = passwd
        self.timeout = float(self.conf_ssh["timeout"])
        self.commands = ["ssh -X node05"]
        self.node = self.conf_ssh["node"]
        # self.pkey = conf_file.PKEY
        self.port = int(self.conf_ssh["port"])
        # self.uploadremotefilepath = conf_file.UPLOADREMOTEFILEPATH
        # self.uploadlocalfilepath = conf_file.UPLOADLOCALFILEPATH
        # self.downloadremotefilepath = conf_file.DOWNLOADREMOTEFILEPATH
        # self.downloadlocalfilepath = conf_file.DOWNLOADLOCALFILEPATH

    def read_config(self):
        self.path = Path(os.getcwd() + "/optimizer/ssh_login/")
        # read config
        with open(self.path / "ssh_config.json") as f:
            self.conf_file = json.load(f)

    def connect(self):
        gateway_session = SSHSession(host=self.host, username=self.username, password=self.password).open()
        remote_session = gateway_session.get_remote_session('node05', password=self.password, timeout=5)
        top_usage = remote_session.get_cmd_output('top -b -n 1') #TODO: check if CPU is clear for calc
        print(top_usage)

        # gateway_session = paramiko.SSHClient()
        # gateway_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # hostname = 'localhost'
        # gateway_session.connect(hostname=self.host, username=self.username, password=self.password,
        #                         timeout=self.timeout)
        # transport = gateway_session.get_transport()
        # ssh_channel = transport.open_channel(
        #     kind="direct-tcpip",
        #     dest_addr=(self.host, self.port),
        #     src_addr=(hostname, self.port),
        #     timeout=self.timeout)


# ---USAGE EXAMPLES
if __name__ == '__main__':
    print("Start of %s" % __file__)

    # Initialize the ssh object
    ssh_obj = Ssh_Util()
    ssh_obj.connect()