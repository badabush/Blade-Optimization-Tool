import numpy as np
import random
import configparser
import json
import pandas as pd
from sphinx.addnodes import index


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


def custom_penalty(fit, beta):
    """

    :param fitnesses: list with (val,) tuples
    :param df:
    :return:
    """
    if feasible(beta):
        return fit

    else:
        # quadratic penalty
        penalty = penalty_distance(beta)
        new_fit = fit[0]
        return (new_fit + penalty,)


def feasible(val):
    """
    Feasibility test for input val (beta).
    :param val:
    :return:
    """
    beta_min = 16.
    beta_max = 17.

    if (val > beta_min) and (val < beta_max):
        return True
    return False


def penalty_distance(val):
    average = 16.5
    return (np.deg2rad(val - average) ** 2) * 25


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


def unravel_individual(checkboxes, dp_genes, individual):
    """
    Matches individuals with name of parameters and user input of free parameters from checkboxes and returns it as a dict so targeting values
    from individual is easier.

    Individual list structure is as follows:
    0 - PP; 1 - AO; 2 - DIV;
    3 - alph11; 4 - alph12;
    5 - alph21; 6 - alph22;
    7 - lambd1; 8 - lambd2;
    9 - th1; 10 - th2;
    11 - xmaxth1; 12 - xmaxth2;
    13 - xmaxcamber1; 14 - xmaxcamber2;
    15 - leth1; 16 - leth2;
    17 - teth1; 18 - teth2

    :param deap_settings:
    :param individual:
    :param dp_genes:
    :return: dict
    """

    df = pd.DataFrame(columns=["id", "blade", "value"]) # {key: individual[i] for }
    full_names = dp_genes.index.tolist()
    checked_params = [key for (key, bool) in checkboxes.items() if bool == 1]
    for i, full_name in enumerate(full_names):
        ID = dp_genes[dp_genes.index == full_name].id.values[0]
        blade = dp_genes[dp_genes.index == full_name].blade.values[0]
        if full_name in checked_params:
            df = df.append({"id": ID, "blade": blade, "value": individual[i]}, ignore_index=True)
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
            df_blade1[row.id] = float(row.value)
            df_blade2[row.id] = float(row.value)
    return df_blade1, df_blade2

def generate_log(idx, df):
    """
    Generate entry for log
    :param idx:
    :param df:
    :return:
    """
    cols = df.columns
    entry = "".join("{key}:{val:.{digits}f}, ".format(key=cols[i], val=val, digits=4) for (i,val) in enumerate(df.iloc[idx].to_list()))

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

if __name__ == '__main__':
    # deapCleanupHandle("10-12-20_14-38-41.log", False)
    read_deap_restraints()
