import threading
import time

import paramiko
from configparser import ConfigParser

from module.optimizer.generate_script import gen_script
from module.optimizer.optimtools import init_xmf_param, read_xmf, calc_xmf

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


        if not self.cb_3point.isChecked():
            self.run_1point()
        else:
            t = threading.Thread(name="3point", target=self.run_3point)
            t.start()
            # self.run_3point()

    def run_1point(self):

        # get node_id, number of cores, writing frequency here
        self.scriptfile = gen_script(self.paths, self.opt_param)
        resfile = "//130.149.110.81/liang/Tandem_Opti/parent_V3/parent_V3_design/parent_V3_design.res"
        xmffile = "//130.149.110.81/liang/Tandem_Opti/parent_V3/parent_V3_design/parent_V3_design.xmf"

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

            t = threading.Thread(name='res_reader', target=self.read_res, args=(resfile, xmffile))
            t.start()

        except (paramiko.ssh_exception.NoValidConnectionsError) as e:
            self.outputbox(e)


    def run_3point(self):
        """
        TODO:
        """
        configfile = "config/three_point_paths.ini"
        config = ConfigParser()
        config.read(configfile)

        paths = self.paths
        # generate scripts for DP, +3deg, -3deg
        scriptfiles = []
        paths['run'] = config['paths']['design']
        scriptfiles.append(gen_script(paths, self.opt_param, suffix="_design"))

        paths['run'] = config['paths']['lower']
        scriptfiles.append(gen_script(paths, self.opt_param, suffix="_lower"))

        paths['run'] = config['paths']['upper']
        scriptfiles.append(gen_script(paths, self.opt_param, suffix="_upper"))
        xmf_files = []
        xmf_files.append(paths['xmf'])
        xmf_files.append(paths['xmf'].replace("design", "lower"))
        xmf_files.append(paths['xmf'].replace("design", "upper"))

        res_files = []
        res_files.append(paths['res'])
        res_files.append(paths['res'].replace("design", "lower"))
        res_files.append(paths['res'].replace("design", "upper"))

        self.res_event.clear()

        # xmf_param = init_xmf_param()
        # run fine131 with script
        if not hasattr(self, 'sshobj'):
            self.ssh_connect()
        if self.sshobj.transport.is_active() == False:
            self.outputbox("Could not find active session.")
            return

        try:
            for i, script in enumerate(scriptfiles):
                self.outputbox("opening FineTurbo..")
                # sending command with display | fine version location | script + location | batch | print
                stdout = self.sshobj.send_cmd(
                    self.display + "/opt/numeca/bin/fine131 -script " + "/home/HLR/" + self.paths['usr_folder'] + "/" +
                    self.paths['proj_folder'] + "/BOT/py_script/" + script + " -batch -print")
                self.outputbox(stdout)

                # change paths of res and xmf files
                t = threading.Thread(name='res_reader', target=self.read_res, args=(res_files[i], xmf_files[i]))
                t.start()
                self.res_event.wait()
                time.sleep(2)
                self.res_event.clear()

            #     xmf_param = read_xmf(xmf_files[i], xmf_param)
            # beta, cp, omega = read_xmf(calc_xmf())
            # print("beta: {}, cp: {}, omega: {}".format(se))
            print(self.xmf_param)

        except (paramiko.ssh_exception.NoValidConnectionsError) as e:
            self.outputbox(e)
