import paramiko
import os, sys
from pathlib import Path
from cryptography.fernet import Fernet
import configparser

# install via pip install jumpssh
from jumpssh import SSHSession


class Ssh_Util:
    """
    Class to connect to SSH.
    """

    def __init__(self):
        self.failure = 0
        self.read_config()
        try:
            self.conf_ssh = self.config["ssh"]

            self.host = self.conf_ssh["host"]
            self.username = self.conf_ssh["user"]
            self.password = self.conf_ssh["passwd"]
            self.key = self.conf_ssh["key"]
            self.timeout = float(self.conf_ssh["timeout"])
            self.commands = ["ssh -X node05"]
            self.node = self.conf_ssh["node"]
            self.port = int(self.conf_ssh["port"])
            # self.ssh_output = None
            # self.ssh_error = None
            # self.client = None
        except AttributeError as e:
            self.failure = 1
            return

    @staticmethod
    def generate_config(username, password, node):
        path = Path(os.getcwd() + "/optimizer/ssh_login/")
        config = configparser.ConfigParser()

        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        ciphered_text = cipher_suite.encrypt(bytes(password, "utf-8"))

        config["ssh"] = {"host": "130.149.110.81",
                         "user": username,
                         "passwd": ciphered_text.decode('utf-8'),
                         "key": key.decode('utf-8'),
                         "node": node,
                         "timeout": "10.0",
                         "port": "22"}

        with open(path / 'ssh_config.ini', 'w') as configfile:
            config.write(configfile)

    def read_config(self):
        """
        Reads in the config.ini file containing login, host and node number information.
        """

        self.path = Path(os.getcwd() + "/optimizer/ssh_login/")

        # read config
        self.config = configparser.ConfigParser()
        try:
            self.config.read(self.path / "ssh_config.ini")
        except ImportError as e:
            self.failure = 1
            print(e)

    def ssh_connect(self):
        """
        Tries to connect to the specific node on the ssh with login information.
        """

        try:
            cipher_suite = Fernet(self.key)
            self.gateway_session = SSHSession(host=self.host, username=self.username,
                                         password=(cipher_suite.decrypt(self.password.encode('utf-8'))).decode('utf-8')).open()
            self.remote_session = self.gateway_session.get_remote_session(self.node,
                                                                password=(cipher_suite.decrypt(self.password.encode('utf-8'))).decode(
                                                                    'utf-8'), timeout=5, )
            return 0
        except ValueError as e:
            return 1

        # pure paramiko approach
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


    def send_cmd(self, cmd):
        """
        Sends command to the ssh-pty and return the stdout.
        """
        try:
            stdout = self.remote_session.get_cmd_output(cmd)
            return stdout

        except AttributeError:
            return None

# if __name__ == '__main__':
#     print("Start of %s" % __file__)
#
#     # Initialize the ssh object
#     ssh_obj = Ssh_Util()
#     ssh_obj.ssh_connect()
