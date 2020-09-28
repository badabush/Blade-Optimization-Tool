from pathlib import Path

def gen_script(dirpath, param):
    """
    Generate the script for running fine turbo.
    """
    scriptname = "script_run.py"
    file = open(dirpath + "/py_script/" + scriptname, "w")
    iec_name = "parent_V3/parent_V3.iec"
    # clean path for usage on the cluster
    if dirpath[0] == "/" and dirpath[1] == "/":
        dirpath = dirpath[1:]
    dirpath = Path(dirpath)
    dirpath = dirpath.parts
    usr_folder = dirpath[-2]
    proj_folder = dirpath[-1]
    scriptpath = "/home/HLR/" + usr_folder + "/" + proj_folder + "/py_script/"
    unixprojpath = "/home/HLR/" + usr_folder + "/" + proj_folder

    task_idx = str(0)
    no_iter = str(param["niter"])
    writing_frequency = str(20)
    file.write('script_version(2.2)\n' +
               'FT.open_project("/home/HLR/' + usr_folder + '/' + proj_folder + '/' + iec_name + '")\n' +
               'FT.set_active_computations([1])\n' +
               'FT.link_mesh_file("/home/HLR/' + usr_folder + '/' + proj_folder + '/Erstes_Netz_Tandem.igg",0)\n' +
               'FT.set_nb_iter_max(' + no_iter + ')\n' +
               'FT.set_output_writing_frequency(' + writing_frequency + ')\n' +
               'FT.save_selected_computations()\n' +
               'FT.task(' + task_idx + ').remove()\n' +
               'FT.new_task()\n' +
               'FT.task(' + task_idx + ').new_subtask()\n' +
               'FT.task(' + task_idx + ').subtask(0).set_run_file("/home/HLR/' + usr_folder + '/' + proj_folder + '/parent_V3/parent_V3_brustinzidenz/parent_V3_brustinzidenz.run")\n' +
               # 'FT.task(' + task_idx + ').start()\n' +
               'FT.task(' + task_idx + ').subtask(0).set_compiler(3)\n' +
               'FT.task(' + task_idx + ').start()'
               )
    file.close()
    return scriptname