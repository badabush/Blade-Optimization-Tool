import paramiko
import os, sys, select
import socket
import logging
import Xlib.support.connect as xlib_connect
import Xlib
from pathlib import Path
from cryptography.fernet import Fernet
import configparser
LOGGER = logging.getLogger(__name__)



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

        # try:
        #     cipher_suite = Fernet(self.key)
        #     self.gateway_session = SSHSession(host=self.host, username=self.username,
        #                                  password=(cipher_suite.decrypt(self.password.encode('utf-8'))).decode('utf-8')).open()
        #     self.remote_session = self.gateway_session.get_remote_session(self.node,
        #                                                         password=(cipher_suite.decrypt(self.password.encode('utf-8'))).decode(
        #                                                             'utf-8'), timeout=5)
        #     # self.remote_session.
        #     return 0
        # except ValueError as e:
        #     return 1

        # pure paramiko approach
        # local_x11_display = xlib_connect.get_display(os.environ['DISPLAY'])
        # local_x11_socket = xlib_connect.get_socket(*local_x11_display[:3])
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
        except ValueError as e:
            return 1
        # session.request_x11(single_connection=True)
        # session.exec_command('xterm')
        # x11_chan = transport.accept()
        #
        # session_fileno = session.fileno()
        # x11_chan_fileno = x11_chan.fileno()
        # local_x11_socket_fileno = local_x11_socket.fileno()
        #
        # poller = select.poll()
        # poller.register(session_fileno, select.POLLIN)
        # poller.register(x11_chan_fileno, select.POLLIN)
        # poller.register(local_x11_socket, select.POLLIN)
        # while not session.exit_status_ready():
        #     poll = poller.poll()
        #     if not poll:  # this should not happen, as we don't have a timeout.
        #         break
        #     for fd, event in poll:
        #         if fd == session_fileno:
        #             while session.recv_ready():
        #                 sys.stdout.write(session.recv(4096))
        #             while session.recv_stderr_ready():
        #                 sys.stderr.write(session.recv_stderr(4096))
        #         if fd == x11_chan_fileno:
        #             local_x11_socket.sendall(x11_chan.recv(4096))
        #         if fd == local_x11_socket_fileno:
        #             x11_chan.send(local_x11_socket.recv(4096))
        #
        # print('Exit status:', session.recv_exit_status())
        # while session.recv_ready():
        #     sys.stdout.write(session.recv(4096))
        # while session.recv_stderr_ready():
        #     sys.stdout.write(session.recv_stderr(4096))
        # session.close()

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
            stdin, stdout, stderr = self.remote_session.exec_command(cmd)
            return stdout.read().decode("utf-8")

        except AttributeError:
            return None

# if __name__ == '__main__':
#     print("Start of %s" % __file__)
#
#     # Initialize the ssh object
#     ssh_obj = Ssh_Util()
#     ssh_obj.ssh_connect()
