from pathlib import Path


def gen_script(paths, param, suffix=""):
    """
    Generate the script for running fine turbo.
    """
    scriptname = "script_run" + suffix + ".py"
    dirpath = paths['dir_raw']
    file = open(dirpath + "/BOT/py_script/" + scriptname, "w")

    task_idx = str(0)
    no_iter = str(param["niter"])
    writing_frequency = str(1000)
    convergence_crit = str(param["convergence"])
    number_of_cores = str(param["cores"])
    node_id = str(param["node"])
    active_computation = 0
    if "lower" in paths['run']:
        active_computation = 1
    elif "upper" in paths['run']:
        active_computation = 2
    str_add_cores = ""

    if suffix == "":
        for i in range(0, int(number_of_cores) - 1):
            str_add_cores += 'FT.task(0).subtask(0).parallelpart_processes_add(1, "' + node_id + '")\n'

        file.write('script_version(2.2)\n' +
                   'FT.open_project("' + paths['iec'] + '")\n' +
                   # 'FT.set_active_computations([1])\n' +
                   'FT.set_active_computations([' + str(active_computation) + '])\n' +
                   # import_geomturbo +
                   'FT.link_mesh_file("' + paths['igg'] + '",0)\n' +
                   'FT.set_nb_iter_max(' + no_iter + ')\n' +
                   'FT.set_output_writing_frequency(' + writing_frequency + ')\n' +
                   'FT.set_convergence_criteria(' + convergence_crit + ')\n' +
                   'FT.save_selected_computations()\n' +
                   'FT.task(' + task_idx + ').remove()\n' +
                   'FT.new_task()\n' +
                   'FT.task(' + task_idx + ').new_subtask()\n' +
                   'FT.task(' + task_idx + ').subtask(0).set_run_file("' + paths['run'] + '")\n' +
                   'FT.task(' + task_idx + ').subtask(0).set_compiler(1)\n' +  # Portland OMPI (PGI6) [0]| Portland OMPI(PGI17) [3]| PORTLAND IMPI (PGI17) [4]| Intel IMPI (ICC15) [1]
                   # 'FT.task(' + task_idx + ').subtask(0).set_parallel_mode(0)\n' +
                   'FT.task(' + task_idx + ').subtask(0).set_parallel_mode(1)\n' +
                   str_add_cores +
                   'FT.task(' + task_idx + ').subtask(0).parallel_automatic_load_balancing()\n' +
                   'FT.task(' + task_idx + ').start()'
                   )
        file.close()
    else:
        print("Automatically set number of cores to 7 cores per subtask (3 subtasks)")
        str_add_cores = []
        for subtask in range(3):
            str_subtask = ""
            for i in range(7-1):
                str_subtask += 'FT.task(0).subtask(' + str(subtask) + ').parallelpart_processes_add(1, "' + node_id + '")\n'
            str_add_cores.append(str_subtask)

        file.write('script_version(2.2)\n' +
                   'FT.open_project("' + paths['iec'] + '")\n' +
                   # 'FT.set_active_computations([1])\n' +
                   'FT.set_active_computations([' + str(active_computation) + '])\n' +
                   # import_geomturbo +
                   'FT.link_mesh_file("' + paths['igg'] + '",0)\n' +
                   'FT.set_nb_iter_max(' + no_iter + ')\n' +
                   'FT.set_output_writing_frequency(' + writing_frequency + ')\n' +
                   'FT.set_convergence_criteria(' + convergence_crit + ')\n' +
                   'FT.save_selected_computations()\n' +
                   'FT.task(' + task_idx + ').remove()\n' +
                   'FT.new_task()\n' +
                   # design
                   'FT.task(' + task_idx + ').new_subtask()\n' +
                   'FT.task(' + task_idx + ').subtask(0).set_condition(0)\n' +
                   'FT.task(' + task_idx + ').subtask(0).set_run_file("' + paths['run_design'] + '")\n' +
                   'FT.task(' + task_idx + ').subtask(0).set_compiler(1)\n' +  # Portland OMPI (PGI6) [0]| Portland OMPI(PGI17) [3]| PORTLAND IMPI (PGI17) [4]| Intel IMPI (ICC15) [1]
                   'FT.task(' + task_idx + ').subtask(0).set_parallel_mode(1)\n' +
                   str_add_cores[0] +
                   'FT.task(' + task_idx + ').subtask(0).parallel_automatic_load_balancing()\n' +
                   'FT.set_nb_iter_max(' + no_iter + ')\n' +
                   'FT.set_output_writing_frequency(' + writing_frequency + ')\n' +
                   'FT.set_convergence_criteria(' + convergence_crit + ')\n' +
                   'FT.save_selected_computations()\n' +
                   # lower
                   'FT.task(' + task_idx + ').new_subtask()\n' +
                   'FT.task(' + task_idx + ').subtask(1).set_condition(0)\n' +
                   'FT.task(' + task_idx + ').subtask(1).set_run_file("' + paths['run_lower'] + '")\n' +
                   'FT.task(' + task_idx + ').subtask(1).set_compiler(1)\n' +  # Portland OMPI (PGI6) [0]| Portland OMPI(PGI17) [3]| PORTLAND IMPI (PGI17) [4]| Intel IMPI (ICC15) [1]
                   'FT.task(' + task_idx + ').subtask(1).set_parallel_mode(1)\n' +
                   str_add_cores[1] +
                   'FT.task(' + task_idx + ').subtask(1).parallel_automatic_load_balancing()\n' +
                   'FT.set_nb_iter_max(' + no_iter + ')\n' +
                   'FT.set_output_writing_frequency(' + writing_frequency + ')\n' +
                   'FT.set_convergence_criteria(' + convergence_crit + ')\n' +
                   'FT.save_selected_computations()\n' +
                   # upper
                   'FT.task(' + task_idx + ').new_subtask()\n' +
                   'FT.task(' + task_idx + ').subtask(2).set_condition(0)\n' +
                   'FT.task(' + task_idx + ').subtask(2).set_run_file("' + paths['run_upper'] + '")\n' +
                   'FT.task(' + task_idx + ').subtask(2).set_compiler(1)\n' +  # Portland OMPI (PGI6) [0]| Portland OMPI(PGI17) [3]| PORTLAND IMPI (PGI17) [4]| Intel IMPI (ICC15) [1]
                   'FT.task(' + task_idx + ').subtask(2).set_parallel_mode(1)\n' +
                   str_add_cores[2] +
                   'FT.task(' + task_idx + ').subtask(2).parallel_automatic_load_balancing()\n' +
                   'FT.set_nb_iter_max(' + no_iter + ')\n' +
                   'FT.set_output_writing_frequency(' + writing_frequency + ')\n' +
                   'FT.set_convergence_criteria(' + convergence_crit + ')\n' +
                   'FT.save_selected_computations()\n' +
                   'FT.task(' + task_idx + ').start()'
                   )
        file.close()
    return scriptname
