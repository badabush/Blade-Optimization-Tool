import threading
import paramiko

from module.optimizer.generate_script import gen_script

class RunHandler:

    def run_script(self):
        """
        TODO:
        """
        # update params from control
        self.update_param()
        # refresh paths
        self.grab_paths()
        # clear plot
        self.optifig_massflow.animate_massflow({})

        if self.box_pathtodir.text() == "":
            self.outputbox("Set Path to Project Directory first!")
            return 0
        # get display address
        self.display = "export DISPLAY=" + self.box_DISPLAY.text() + ";"

        # get node_id, number of cores, writing frequency here
        self.scriptfile = gen_script(self.paths, self.opt_param)

        # run fine131 with script
        if not hasattr(self, 'sshobj'):
            self.ssh_connect()
        if self.sshobj.transport.is_active() == False:
            self.outputbox("Could not find active session.")
            return
        try:
            self.outputbox("opening FineTurbo..")
            # sending command with display | fine version location | script + location | batch | print
            stdout = self.sshobj.send_cmd(
                self.display + "/opt/numeca/bin/fine131 -script " + "/home/HLR/" + self.paths['usr_folder'] + "/" +
                self.paths['proj_folder'] + "/BOT/py_script/" + self.scriptfile + " -batch -print")
            self.outputbox(stdout)

            t = threading.Thread(name='res_reader', target=self.read_res)
            t.start()

        except (paramiko.ssh_exception.NoValidConnectionsError) as e:
            self.outputbox(e)