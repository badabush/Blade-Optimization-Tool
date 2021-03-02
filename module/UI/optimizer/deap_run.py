# import threading
# import time
# from configparser import ConfigParser
#
# from module.optimizer.generate_script import gen_script
#
# class DeapScripts:
#     def deaprun_with_log(self):
#         pass
#
#     def deap_one_point(self):
#         """
#         TODO: onepoint run is not in the code rn, but can be taken from run_handle
#         """
#         # update params from control
#         self.update_param()
#         # refresh paths
#         self.grab_paths()
#         # clear plot
#         self.optifig_massflow.animate_massflow({})
#         # self.optifig_xmf.animate_xmf({})
#         # self.optifig_xmf.clear()
#
#         if self.box_pathtodir.text() == "":
#             self.outputbox("Set Path to Project Directory first!")
#             return 0
#         # get display address
#         self.display = "export DISPLAY=" + self.box_DISPLAY.text() + ";"
#
#         # get node_id, number of cores, writing frequency here
#         self.scriptfile = gen_script(self.paths, self.opt_param)
#
#         # run fine131 with script
#         if not hasattr(self, 'sshobj'):
#             self.ssh_connect()
#         if self.sshobj.transport.is_active() == False:
#             self.outputbox("Could not find active session.")
#             return
#         try:
#             self.outputbox("opening FineTurbo..")
#             # sending command with display | fine version location | script + location | batch | print
#             stdout = self.sshobj.send_cmd(
#                 self.display + "/opt/numeca/bin/fine131 -script " + "/home/HLR/" + self.paths['usr_folder'] + "/" +
#                 self.paths['proj_folder'] + "/BOT/py_script/" + self.scriptfile + " -batch -print")
#             self.outputbox(stdout)
#
#             # start thread to read res file
#             resfile = "//130.149.110.81/liang/Tandem_Opti/parent_V3/parent_V3_design/parent_V3_design.res"
#             xmffile = "//130.149.110.81/liang/Tandem_Opti/parent_V3/parent_V3_design/parent_V3_design.xmf"
#             t = threading.Thread(name='res_reader', target=self.read_res, args=(resfile, xmffile))
#             t.start()
#
#         except (TimeoutError) as e:
#             # if timeout error, kill all tasks and try again
#             print(e)
#             self.outputbox("Fine didnt start properly. Killing tasks and retrying..")
#             self.kill_loop()
#             time.sleep(15)
#             self.outputbox("Retrying..")
#             # sending command with display | fine version location | script + location | batch | print
#             stdout = self.sshobj.send_cmd(
#                 self.display + "/opt/numeca/bin/fine131 -script " + "/home/HLR/" + self.paths['usr_folder'] + "/" +
#                 self.paths['proj_folder'] + "/BOT/py_script/" + self.scriptfile + " -batch -print")
#             self.outputbox(stdout)
#
#             # start thread to read res file
#             t = threading.Thread(name='res_reader', target=self.read_res)
#             t.start()
#
#
