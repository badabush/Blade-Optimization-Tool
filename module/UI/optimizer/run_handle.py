import threading
import time
import os

import paramiko
from configparser import ConfigParser

from optimizer.generate_script import gen_script
from optimizer.optimtools import read_xmf
from UI.optimizer.deap_settings_handle import DeapSettingsHandle
from optimizer.genetic_algorithm.deaptools import read_deap_restraints, ind_list_from_datasets


class RunHandler:

    def deaprun_with_log(self):
        """
        When UI button 'Continue Log' is pressed, open file explorer for log file and run GA.
        :return:
        """
        try:
            ds_log_meta = self.load_log()
        except IOError as e:
            self.outputbox(str(e))
            return

        self.deap_config_ui.get_checkbox()
        self.deap_config_ui.get_values()
        dp_genes = read_deap_restraints()
        deap_settings = DeapSettingsHandle(self.deap_config_ui, dp_genes)
        ds_curr = deap_settings.values
        # assert parameters between log file and UI settings
        if not ds_log_meta:
            return

        try:
            if not ds_log_meta["version"] == self.VERSION:
                raise AssertionError(
                    "Software version don't match (Current:{curr}, Log:{log})".format(curr=self.VERSION,
                                                                                      log=ds_log_meta["version"]))

            if not ds_log_meta["POP_SIZE"] == ds_curr["pop_size"]:
                raise AssertionError(
                    "Population size don't match (Current:{curr}, Log:{log})".format(log=ds_log_meta["POP_SIZE"],
                                                                                     curr=ds_curr["pop_size"]))

            if not ds_log_meta["CXPB"] == ds_curr["cxpb"]:
                raise AssertionError(
                    "CXPB don't match (Current:{curr}, Log:{log})".format(log=ds_log_meta["CXPB"],
                                                                          curr=ds_curr["cxpb"]))

            if not ds_log_meta["MUTPB"] == ds_curr["mutpb"]:
                raise AssertionError(
                    "MUTPB don't match (Current:{curr}, Log:{log})".format(log=ds_log_meta["MUTPB"],
                                                                           curr=ds_curr["mutpb"]))

            if not ds_log_meta["PENALTY_FACTOR"] == ds_curr["penalty_factor"]:
                raise AssertionError(
                    "Penalty factor don't match (Current:{curr}, Log:{log})".format(log=ds_log_meta["PENALTY_FACTOR"],
                                                                                    curr=ds_curr["penalty_factor"]))

            if not ds_log_meta["random_seed"] == ds_curr["random_seed"]:
                raise AssertionError(
                    "Penalty factor don't match (Current:{curr}, Log:{log})".format(log=ds_log_meta["random_seed"],
                                                                                    curr=ds_curr["random_seed"]))

            curr_free_params = [key for key, val in deap_settings.checkboxes.items() if val == 1]
            if not ds_log_meta["free_params"].sort() == curr_free_params.sort():
                raise AssertionError("Free parameters don't match.")

            if not ds_log_meta["objective_params"] == ds_curr["objective_params"]:
                raise AssertionError(
                    "Penalty factor don't match (Current:{curr}, Log:{log})".format(log=ds_log_meta["objective_params"],
                                                                                    curr=ds_curr["objective_params"]))

            if not ds_log_meta["beta_constraint"] == ds_curr["beta_constraint"]:
                raise AssertionError(
                    "Beta Constraint don't match (Current:{curr}, Log:{log})".format(
                        log=ds_log_meta["beta_constraint"], curr=ds_curr["beta_constraint"]))

            if not ds_log_meta["beta_constraint_range"] == ds_curr["beta_constraint_range"]:
                raise AssertionError(
                    "Beta Constraint Range don't match (Current:{curr}, Log:{log})".format(
                        log=ds_log_meta["beta_constraint_range"], curr=ds_curr["beta_constraint_range"]))


            ref_individual = ind_list_from_datasets(self.ds1, self.ds2, dp_genes)
            for i, (key, val) in enumerate(ds_log_meta["ref_params"].items()):
                if not ref_individual[i] == val:
                    print("False")
                    raise AssertionError(
                        "{key} don't match (Current:{curr}, Log:{log})".format(key=key, log=val,
                                                                               curr=ref_individual[i]))

        except AssertionError as e:

            self.outputbox(
                "AssertionError: Log file and user settings don't match. Aborting 'Continue log', back to idle.")
            self.outputbox(e.__str__())
            return

        self.ds_log_meta = ds_log_meta
        self.ga_run(log_loaded=True)

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

        paths = self.paths
        paths['run_design'] = self.config_3point['paths']['design']
        paths['run_lower'] = self.config_3point['paths']['lower']
        paths['run_upper'] = self.config_3point['paths']['upper']
        scriptfile = gen_script(paths, self.opt_param, suffix="_simultaneous")

        self.res_event.clear()

        # try removing all res files
        for i in range(3):
            try:
                os.remove(self.res_files[i])
            except (FileNotFoundError, PermissionError):
                print("No .res file removed.")

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
                self.display + "/opt/numeca/bin/fine131 -script " + "/home/HLR/" + paths['usr_folder'] + "/" +
                paths['proj_folder'] + "/BOT/py_script/" + scriptfile + " -batch -print")
            self.outputbox(stdout)

            # for i in range(3):
            # try removing old res files
            # change paths of res and xmf files
            t = threading.Thread(name='res_reader', target=self.read_res, args=(self.res_files[0], self.xmf_files[0]),
                                 daemon=True)
            t.start()
            self.res_event.wait()
            time.sleep(2)
            # self.res_event.clear()
            # self.res_event.set()
            # read xmfs from lower and upper point
            self.xmf_param_lower = read_xmf(self.xmf_files[1], self.xmf_param_lower)
            self.xmf_param_upper = read_xmf(self.xmf_files[2], self.xmf_param_upper)

        except (TimeoutError) as e:
            print(e)
