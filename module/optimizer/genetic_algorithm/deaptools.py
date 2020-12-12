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


if __name__ == '__main__':
    # deapCleanupHandle("10-12-20_14-38-41.log", False)
    read_deap_restraints()
