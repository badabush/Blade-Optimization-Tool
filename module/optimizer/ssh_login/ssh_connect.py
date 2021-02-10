import paramiko
import os
import logging

from pathlib import Path
from cryptography.fernet import Fernet
import configparser
LOGGER = logging.getLogger(__name__)



class SshUtil:
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
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            cipher_suite = Fernet(self.key)
            ssh_client.connect(hostname=self.host, username=self.username, password=(cipher_suite.decrypt(self.password.encode('utf-8'))).decode('utf-8'),
                                    timeout=self.timeout)
            # transport = ssh_client.get_transport()
            self.transport = ssh_client.get_transport()
            session = self.transport.open_channel("direct-tcpip", (self.node, 22), (self.host, 22))

            self.remote_session = paramiko.SSHClient()
            self.remote_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.remote_session.connect(self.node, username=self.username, password=(cipher_suite.decrypt(self.password.encode('utf-8'))).decode('utf-8'), sock=session)

            return 0
        except ValueError:
            return 1

    def send_cmd(self, cmd):
        """
        Sends command to the ssh-pty and return the stdout.
        """
        try:
            stdin, stdout, stderr = self.remote_session.exec_command(cmd)
            return stdout.read().decode("utf-8")

        except AttributeError:
            return None
