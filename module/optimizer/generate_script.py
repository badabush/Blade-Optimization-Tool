from pathlib import Path


def gen_script(paths, param, load_blade):
    """
    Generate the script for running fine turbo.
    """
    scriptname = "script_run.py"
    dirpath = paths['dir_raw']
    file = open(dirpath + "/BOT/py_script/" + scriptname, "w")

    task_idx = str(0)
    no_iter = str(param["niter"])
    writing_frequency = str(20)
    if load_blade:
        geomturbo_path = ""
        import_geomturbo = 'import_geomturbo_file("' + geomturbo_path + '")\n'
    else:
        import_geomturbo = ""

    file.write('script_version(2.2)\n' +
               'FT.open_project("/home/HLR/' + paths['usr_folder'] + '/' + paths['proj_folder'] + '/' + paths['iec'] + '")\n' +
               'FT.set_active_computations([1])\n' +
                # import_geomturbo +
               'FT.link_mesh_file("/home/HLR/' + paths['usr_folder'] + '/' + paths['proj_folder'] + '/' + paths['igg'] + '",0)\n' +
               'FT.set_nb_iter_max(' + no_iter + ')\n' +
               'FT.set_output_writing_frequency(' + writing_frequency + ')\n' +
               'FT.save_selected_computations()\n' +
               'FT.task(' + task_idx + ').remove()\n' +
               'FT.new_task()\n' +
               'FT.task(' + task_idx + ').new_subtask()\n' +
               'FT.task(' + task_idx + ').subtask(0).set_run_file("/home/HLR/' + paths['usr_folder'] + '/' +
               paths['proj_folder'] + '/' + paths['run'] + '")\n' +
               'FT.task(' + task_idx + ').subtask(0).set_compiler(3)\n' +
               'FT.task(' + task_idx + ').start()'
               )
    file.close()
    return scriptname
