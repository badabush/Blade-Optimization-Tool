import numpy as np
import random
import configparser
import json
import pandas as pd


def _random(min, max, digits):
    """
    Random float between min and max, rounded to input digits. Returns random number in boundary with given digits.

    :param min: lower boundary
    :param max: upper boundary
    :param digits: number of digits of generated number
    :return: float
    """

    return np.round(random.uniform(min, max), digits)


def read_deap_restraints():
    """
    Reads config file (.ini) for DEAP genes and restraints. Returns dataframe.

    :return: pd.DataFrame
    """

    config = configparser.ConfigParser()
    config.read("config/deap_restraints.ini")
    keys = json.loads(config.get('key', 'keys'))
    # create empty pandas frame
    df = pd.DataFrame(data=None, index=[section for section in config.sections() if section != "key"], columns=keys)
    for section in config.sections():
        if section == "key":
            continue
        for option in config.options(section):
            # print("{0}:::{1}".format(option, config.get(section, option)))
            df.loc[section, option] = config.get(section, option)
    return df


def custom_penalty(fit, beta, penalty_factor, beta_default=16.5, beta_range_default=.5):
    """

    :param fitnesses: list with (val,) tuples
    :param df:
    :return:
    """
    if feasible(beta, beta_default, beta_range_default):
        return fit

    else:
        # quadratic penalty
        penalty = penalty_distance(beta, penalty_factor, beta_default)
        new_fit = fit[0]
        return (np.round(new_fit + penalty, 4),)


def feasible(val, default, range):
    """
    Feasibility test for input val (beta).
    :param val:
    :return:
    """
    beta_min = default-range
    beta_max = default+range

    if (val > beta_min) and (val < beta_max):
        return True
    return False


def penalty_distance(val, penalty_factor=40, beta=16.5):
    return (np.deg2rad(val - beta) ** 2) * penalty_factor


def get_three_point_paths(paths):
    configfile = "config/three_point_paths.ini"
    config = configparser.ConfigParser()
    config.read(configfile)

    xmf_files = []
    xmf_files.append(paths['xmf'])
    xmf_files.append(paths['xmf'].replace("design", "lower"))
    xmf_files.append(paths['xmf'].replace("design", "upper"))

    res_files = []
    res_files.append(paths['res'])
    res_files.append(paths['res'].replace("design", "lower"))
    res_files.append(paths['res'].replace("design", "upper"))
    return xmf_files, res_files, config


def ind_list_from_datasets(ds1, ds2, genes):
    """
    Generate a list from datasets, mimicing the 'individual' list. Required for calculating reference Blade.
    :param ds1:
    :param ds2:
    :return:
    """
    indlist = []
    for key in genes.index:
        ds_id = genes.loc[key].id
        blade = int(genes.loc[key].blade)
        if blade == 0:
            indlist.append(ds1[ds_id])
        elif blade == 1:
            indlist.append(ds1[ds_id])
        elif blade == 2:
            indlist.append(ds2[ds_id])

    return indlist


def unravel_individual(checkboxes, dp_genes, individual):
    """
    Matches individuals with name of parameters and user input of free parameters from checkboxes and returns it as a dict so targeting values
    from individual is easier.

    Individual list structure is as follows:
    0 - PP; 1 - AO; 2 - DIV; 3 - cdist;
    4 - alph11; 5 - alph12;
    6 - alph21; 7 - alph22;
    8 - lambd1; 9 - lambd2;
    10 - th1; 11 - th2;
    12 - xmaxth1; 13 - xmaxth2;
    14 - xmaxcamber1; 15 - xmaxcamber2;
    16 - leth1; 17 - leth2;
    18 - teth1; 19 - teth2

    :param deap_settings:
    :param individual:
    :param dp_genes:
    :return: dict
    """

    df = pd.DataFrame(columns=["id", "blade", "value"])  # {key: individual[i] for }
    full_names = dp_genes.index.tolist()
    checked_params = [key for (key, bool) in checkboxes.items() if bool == 1]
    for i, full_name in enumerate(full_names):
        ID = dp_genes[dp_genes.index == full_name].id.values[0]
        blade = dp_genes[dp_genes.index == full_name].blade.values[0]
        if full_name in checked_params:
            digit = int(dp_genes[dp_genes.index == full_name].digits.values[0])
            df = df.append({"id": ID, "blade": blade, "value": np.round(individual[i], digit)}, ignore_index=True)
    df.index = checked_params

    # print("alph1 blade1: {0}, alph2 blade1: {1}".format(individual[3], individual[4]))
    # print("alph1 blade2: {0}, alph2 blade2: {1}".format(individual[5], individual[6]))
    return df


def get_row(individuals):
    """
    Generate row for df from individuals for logging.

    :param individuals:
    :return: DataSeries
    """
    return individuals.value.to_dict()


def update_blade_individuals(df_blade1, df_blade2, df_ind):
    for i, row in df_ind.iterrows():
        if int(row.blade) == 1:
            df_blade1[row.id] = float(row.value)
        elif int(row.blade) == 2:
            df_blade2[row.id] = float(row.value)
        else:
            if not row.id == "cdist":
                df_blade1[row.id] = float(row.value)
                df_blade2[row.id] = float(row.value)
            else:
                df_blade1[row.id] = float(row.value)
                df_blade2[row.id] = 1-float(row.value)
    return df_blade1, df_blade2


def generate_log(idx, df, gen=0):
    """
    Generate entry for log
    :param idx:
    :param df:
    :return:
    """
    try:
        df_gen = int(df.generation.iloc[idx])
    except ValueError:
        df_gen = 0
    cols = df.columns
    entry = "".join("{key}:{val:.{digits}f}, ".format(key=cols[i], val=val, digits=4) for (i, val) in
                    enumerate(df.iloc[idx].to_list()))
    if (gen != 0) and (gen > df_gen):
        entry = entry.replace("generation:{df_gen}".format(df_gen=df_gen), "generation:{gen}".format(gen=gen))
    return entry[:-2]


def init_deap_df(checkboxes, threepoint_checked):
    cols = [key for (key, bool) in checkboxes.items() if bool == 1]
    if threepoint_checked:
        cols.append("beta")
        cols.append("beta_lower")
        cols.append("beta_upper")
        cols.append("omega")
        cols.append("omega_lower")
        cols.append("omega_upper")
        cols.append("cp")
        cols.append("cp_lower")
        cols.append("cp_upper")
    else:
        cols.append("beta")
        cols.append("omega")
        cols.append("cp")
    cols.append("fitness")
    cols.append("generation")
    df = pd.DataFrame(columns=cols)
    return df


def read_header(log_path):
    """
    Extract meta data from logfile. Returns dictionary of data.
    :param logfile:
    :return: log_meta
    :rtype dict
    """
    log_meta = {}
    with open(log_path, "r") as f:
        lines = f.readlines(2000)
        for line in lines:
            line = line.strip("\n")
            if "SOFTWARE VERSION" in line:
                chunk = line.split(":")
                log_meta["version"] = chunk[-1]
            elif "POP_SIZE" in line:
                chunk = line.split("--- ")[-1]
                chunk = chunk.replace(" ", "")
                chunklist = chunk.split(",")
                temp_dict = {elem.split(":")[0]: float(elem.split(":")[1]) for elem in chunklist}
                log_meta.update(temp_dict)
                del temp_dict
            elif "Free Parameters" in line:
                chunk = line.split(":")[-1]
                chunk = chunk.replace(" ", "")
                chunklist = chunk.split(",")
                log_meta["free_params"] = chunklist
            elif "RANDOM SEED" in line:
                chunk = line.split("--- ")[-1]
                log_meta["random_seed"] = int(chunk.split(":")[-1])
            elif "Objective function parameters" in line:
                chunk = line.split("--- ")[-1]
                chunk = chunk.lstrip("Objective function parameters: ")
                chunklist = chunk.replace(" ", "").split(",")
                log_meta["objective_params"] = [float(elem.split(":")[-1]) for elem in chunklist]
            elif "Reference Blade parameters" in line:
                chunk = line.split("--- ")[-1]
                chunk = chunk.split("Reference Blade parameters: ")[-1]
                chunklist = chunk.replace(" ", "").split(",")
                log_meta["ref_params"] = {elem.split(":")[0]: float(elem.split(":")[1]) for elem in chunklist}
            elif "Reference Blade Fitness" in line:
                log_meta["ref_fit"] = float(line.split(":")[-1])
            elif "Beta Constraint" in line:
                chunk = line.split("--- ")[-1]
                chunklist = chunk.split(", ")
                log_meta["beta_constraint"] = float(chunklist[0].lstrip("Beta Constraint: "))
                log_meta["beta_constraint_range"] = float(chunklist[1].lstrip("Beta Constraint Range: "))
    return log_meta


if __name__ == '__main__':
    # deapCleanupHandle("10-12-20_14-38-41.log", False)
    read_deap_restraints()
