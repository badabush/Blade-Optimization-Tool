import base64
import paramiko

def ssh_cmd(address, usr, pwd, command):
    try:
        print("ssh " + usr + "@" + address + ", running : " +
              command)
        client = paramiko.SSHClient()
        client.load_system_host_keys()  # this loads any local ssh keys
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(address, username=usr, password=pwd)
        _, ss_stdout, ss_stderr = client.exec_command(command)
        r_out, r_err = ss_stdout.readlines(), ss_stderr.read()
        print(r_err)
        if len(r_err) > 5:
            print(r_err)
        else:
            print(r_out)
        client.close()
    except IOError:
        print(".. host " + address + " is not up")
        return "host not up", "host not up"