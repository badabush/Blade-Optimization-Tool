import threading
import time
from configparser import ConfigParser

from module.optimizer.generate_script import gen_script

class DeapScripts:
    #
    # def deap_three_point(self):
    #     """
    #     TODO:
    #     """
    #     # update params from control
    #     self.update_param()
    #     # refresh paths
    #     self.grab_paths()
    #     # clear plot
    #     self.optifig_massflow.animate_massflow({})
    #
    #     if self.box_pathtodir.text() == "":
    #         self.outputbox("Set Path to Project Directory first!")
    #         return 0
    #     # get display address
    #     self.display = "export DISPLAY=" + self.box_DISPLAY.text() + ";"
    #
    #     paths = self.paths
    #     # get node_id, number of cores, writing frequency here
    #     # scriptfiles = []
    #     #
    #     # paths['run'] = self.config_3point['paths']['design']
    #     # scriptfiles.append(gen_script(paths, self.opt_param, suffix="_design"))
    #     #
    #     # paths['run'] = self.config_3point['paths']['lower']
    #     # scriptfiles.append(gen_script(paths, self.opt_param, suffix="_lower"))
    #     #
    #     # paths['run'] = self.config_3point['paths']['upper']
    #     # scriptfiles.append(gen_script(paths, self.opt_param, suffix="_upper"))
    #     paths['run_design'] = self.config_3point['paths']['design']
    #     paths['run_lower'] = self.config_3point['paths']['lower']
    #     paths['run_upper'] = self.config_3point['paths']['upper']
    #     scriptfile = gen_script(paths, self.opt_param, suffix="_design")
    #
    #     self.res_event.clear()
    #
    #     # run fine131 with script
    #     if not hasattr(self, 'sshobj'):
    #         self.ssh_connect()
    #     if self.sshobj.transport.is_active() == False:
    #         self.outputbox("Could not find active session.")
    #         return
    #     try:
    #
    #         self.outputbox("opening FineTurbo..")
    #         # sending command with display | fine version location | script + location | batch | print
    #         stdout = self.sshobj.send_cmd(
    #             self.display + "/opt/numeca/bin/fine131 -script " + "/home/HLR/" + paths['usr_folder'] + "/" +
    #             paths['proj_folder'] + "/BOT/py_script/" + scriptfile + " -batch -print")
    #         self.outputbox(stdout)
    #
    #         for i in range(3):
    #             # change paths of res and xmf files
    #             t = threading.Thread(name='res_reader', target=self.read_res, args=(self.res_files[i], self.xmf_files[i]))
    #             t.start()
    #             self.res_event.wait()
    #             time.sleep(2)
    #             self.res_event.clear()
    #         self.res_event.set()
    #
    #     except (TimeoutError) as e:
    #         # if timeout error, kill all tasks and try again
    #         print(e)
    #         # self.outputbox("Fine didnt start properly. Killing tasks and retrying..")
    #         # self.kill_loop()
    #         # time.sleep(15)
    #         # self.outputbox("Retrying..")
    #         # for i, script in enumerate(scriptfiles):
    #         #     self.outputbox("opening FineTurbo..")
    #         #     # sending command with display | fine version location | script + location | batch | print
    #         #     stdout = self.sshobj.send_cmd(
    #         #         self.display + "/opt/numeca/bin/fine131 -script " + "/home/HLR/" + paths['usr_folder'] + "/" +
    #         #         paths['proj_folder'] + "/BOT/py_script/" + script + " -batch -print")
    #         #     self.outputbox(stdout)
    #         #
    #         #     # change paths of res and xmf files
    #         #     t = threading.Thread(name='res_reader', target=self.read_res, args=(self.res_files[i], self.xmf_files[i]))
    #         #     t.start()
    #         #     self.res_event.wait()
    #         #     time.sleep(2)
    #         #     self.res_event.clear()
    #         # self.res_event.set()

    def deap_one_point(self):
        """
        TODO:
        """
        # update params from control
        self.update_param()
        # refresh paths
        self.grab_paths()
        # clear plot
        self.optifig_massflow.animate_massflow({})
        # self.optifig_xmf.animate_xmf({})
        # self.optifig_xmf.clear()

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

            # start thread to read res file
            resfile = "//130.149.110.81/liang/Tandem_Opti/parent_V3/parent_V3_design/parent_V3_design.res"
            xmffile = "//130.149.110.81/liang/Tandem_Opti/parent_V3/parent_V3_design/parent_V3_design.xmf"
            t = threading.Thread(name='res_reader', target=self.read_res, args=(resfile, xmffile))
            t.start()

        except (TimeoutError) as e:
            # if timeout error, kill all tasks and try again
            print(e)
            self.outputbox("Fine didnt start properly. Killing tasks and retrying..")
            self.kill_loop()
            time.sleep(15)
            self.outputbox("Retrying..")
            # sending command with display | fine version location | script + location | batch | print
            stdout = self.sshobj.send_cmd(
                self.display + "/opt/numeca/bin/fine131 -script " + "/home/HLR/" + self.paths['usr_folder'] + "/" +
                self.paths['proj_folder'] + "/BOT/py_script/" + self.scriptfile + " -batch -print")
            self.outputbox(stdout)

            # start thread to read res file
            t = threading.Thread(name='res_reader', target=self.read_res)
            t.start()


