import pandas as pd
from pathlib import Path
import xmltodict
import time
import random
import xml

import numpy as np

def read_top_usage(top_usage):
    """
    Cleans up the stdout from the command top. Does the formatting into lines, dropping header,
    packing into a pdDataFrame, sorting cpu (descending) and dropping some columns w/ unneccessary information.
    """

    ss = top_usage.split('\n')
    msg = []
    for i in range(6, len(ss)):
        line = ss[i].split()
        msg.append(line)
    df = pd.DataFrame(data=msg,columns=msg[0])
    df = df.drop(df.head(5).index) # drop first 5 rows
    df['%CPU'] = df['%CPU'].astype('float')
    df['%MEM'] = df['%MEM'].astype('float')
    df.sort_values(by=['%CPU'], ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    # drop some columns
    df.drop(columns=["PR", "NI", "VIRT", "RES", "SHR", "S"], inplace=True)
    return df

def read_by_token(fileobj):
    """
    A generator. Reads lines, drops everything except tokens (str, values, etc.) and appends to a list. Yields list.
    """
    for line in fileobj:
        ds = []
        if not line:
            time.sleep(.1)
            continue
        for token in line.split():
            ds.append(token)
        yield ds

def parse_res(file, q, event):
    """
    Worker thread to read new lines from res. Only queues relevant lines.
    """

    with open(file, 'r') as fp:
        while not event.is_set():
            tokenized = read_by_token(fp)
            for token in tokenized:
                if token[0].isdigit() and len(token) > 1:
                    q.put(token)
            time.sleep(.1)

        try:
            fp.close()
        except FileNotFoundError:
            print('Could not close file.')
            pass
        time.sleep(5)

def init_xmf_param():
    """
    Returns an empty form of dict with lists fitting the read_xmf and calc_xmf format.
    :return:
    """

    xmf_param = {}  # [['Inlet', Outlet'], ...]
    xmf_param['abs_total_pressure'] = []
    xmf_param['static_pressure'] = []
    xmf_param['y_velocity'] = []
    xmf_param['z_velocity'] = []
    return xmf_param


def read_xmf(file, param):
    try:
        with open(file) as f:
            doc = xmltodict.parse(f.read())
            doclist = list(doc.items())
            param['abs_total_pressure'].append([
                float(doclist[0][1]['Station'][0]['Condition'][1]['float'][0]['#text']),
                float(doclist[0][1]['Station'][1]['Condition'][1]['float'][0]['#text'])
            ])
            param['static_pressure'].append([
                float(doclist[0][1]['Station'][0]['Condition'][0]['float'][0]['#text']),
                float(doclist[0][1]['Station'][1]['Condition'][0]['float'][0]['#text'])
            ])
            param['y_velocity'].append([
                float(doclist[0][1]['Station'][0]['Velocity']['float'][1]['#text']),
                float(doclist[0][1]['Station'][1]['Velocity']['float'][1]['#text'])
            ])
            param['z_velocity'].append([
                float(doclist[0][1]['Station'][0]['Velocity']['float'][2]['#text']),
                float(doclist[0][1]['Station'][1]['Velocity']['float'][2]['#text'])
            ])
    except (KeyError, IndexError, xml.parsers.expat.ExpatError) as e:
        print("Error reading xmf file.")
        print(e)
    return param

def cleanpaths(path_dict):
    """
    Cleans up input paths for usage in generate_script and optimhandle.
    """

    paths = {}
    paths['dir_raw'] = path_dict['dir']
    if path_dict['dir'][0] == "/" and path_dict['dir'][1] == "/":
        paths['dir'] = Path(path_dict['dir'][1:]).parts
    paths['usr_folder'] = paths['dir'][-2]
    paths['proj_folder'] = paths['dir'][-1]
    unix_projpath = "/home/HLR/" + paths['usr_folder'] + '/' + paths['proj_folder']
    paths['iec'] = path_dict['iec'].replace(paths['dir_raw'], unix_projpath)
    paths['igg'] = path_dict['igg'].replace(paths['dir_raw'], unix_projpath)
    paths['run'] = path_dict['run'].replace(paths['dir_raw'], unix_projpath)

    # res and xmf are in run folder

    paths['res'] = path_dict['run'].replace(Path(paths['run']).parts[-1], Path(paths['run']).parts[-1].replace('run', 'res'))
    paths['xmf'] = path_dict['run'].replace(Path(paths['run']).parts[-1], Path(paths['run']).parts[-1].replace('run', 'xmf'))

    return paths



def calc_xmf(ds):
    """
    ds is a nested dict with lists where entries y_velocity, z_velocity, static_pressure and abs_total_pressure must exist.
    TODO:
    """
    #TODO: modified for DEAP run
    y_vel = np.array(ds['y_velocity'])
    z_vel = np.array(ds['z_velocity'])
    p_stat = np.array(ds['static_pressure'])
    p_atot = np.array(ds['abs_total_pressure'])
    beta = np.array(
        list(map(lambda y, z: np.arcsin(y[1] / z[1]) if (z[1] > 1) and (y[1] > 1) else 0, y_vel, z_vel)))
    cp = np.array(
        list(map(lambda ps, pt: (ps[1] - ps[0]) / (pt[0] - ps[0]) if np.abs(
            (ps[1] - ps[0]) / (pt[0] - ps[0])) < 1 else 0,
                 p_stat, p_atot)))
    omega = np.array(
        list(map(lambda ps, pt: (pt[0] - pt[1]) / (pt[0] - ps[0]) if np.abs(
            (pt[0] - pt[1]) / (pt[0] - ps[0])) < 1 else 0,
                 p_stat, p_atot)))
    return beta, cp, omega

def status_convergence(file):
    """
    Reads the last line of the logfile and checks, if the convergence criterion has been satisfied. Returns the status
    """
    with open(file) as f:
        for line in (f.readlines() [-1:]):
            # print(line, end='')
            if "CONVERGENCE CRITERIA SATISFIED" in line:
                f.close()
                return True
            else:
                f.close()
                return False


if __name__ == "__main__":
    f = "//130.149.110.81/liang/Tandem_Opti/parent_V3/parent_V3_design/parent_V3_design.xmf"

    # status_convergence(f)
    # init XMF dict
    xmf_param = {'abs_total_pressure': [[105600.0, 101364.7], [105600.0, 101364.7], [105600.0, 102406.1], [105600.0, 102406.1],
                            [105600.0, 103595.2], [105600.0, 103595.2], [105600.0, 104175.0], [105600.0, 104175.0],
                            [105600.0, 104425.2], [105600.0, 104425.2], [105600.0, 104611.6], [105600.0, 101364.7],
                            [105600.0, 101364.7], [105600.0, 102468.1], [105600.0, 102468.1], [105600.0, 103712.2],
                            [105600.0, 103712.2], [105600.0, 104286.8], [105600.0, 104286.8], [105600.0, 104527.9],
                            [105600.0, 104527.9], [105600.0, 104696.6], [105600.0, 101364.7], [105600.0, 101364.7],
                            [105600.0, 102335.7], [105600.0, 102335.7], [105600.0, 103451.1], [105600.0, 103451.1],
                            [105600.0, 104028.0], [105600.0, 104028.0], [105600.0, 104283.7], [105600.0, 104283.7],
                            [105600.0, 104481.4]],
     'static_pressure': [[105539.2, 101300.0], [105539.2, 101300.0], [102802.4, 101300.0], [102802.4, 101300.0],
                         [100831.1, 101300.0], [100831.1, 101300.0], [99468.94, 101300.0], [99468.94, 101300.0],
                         [98559.98, 101300.0], [98559.98, 101300.0], [97982.87, 101300.0], [105539.2, 101300.0],
                         [105539.2, 101300.0], [102962.3, 101300.0], [102962.3, 101300.0], [101201.0, 101300.0],
                         [101201.0, 101300.0], [100019.2, 101300.0], [100019.2, 101300.0], [99270.4, 101300.0],
                         [99270.4, 101300.0], [98801.93, 101300.0], [105539.2, 101300.0], [105539.2, 101300.0],
                         [102633.2, 101300.0], [102633.2, 101300.0], [100420.8, 101300.0], [100420.8, 101300.0],
                         [98883.14, 101300.0], [98883.14, 101300.0], [97815.42, 101300.0], [97815.42, 101300.0],
                         [97130.0, 101300.0]],
     'y_velocity': [[7.87988, 0.0], [7.87988, 0.0], [53.7252, 9.715643], [53.7252, 9.715643], [70.37945, 22.47122],
                    [70.37945, 22.47122], [79.99231, 26.5211], [79.99231, 26.5211], [85.85571, 25.59814],
                    [85.85571, 25.59814], [89.39766, 25.50819], [7.546852, 0.0], [7.546852, 0.0], [49.94902, 10.35884],
                    [49.94902, 10.35884], [64.69669, 23.64353], [64.69669, 23.64353], [73.0219, 27.48052],
                    [73.0219, 27.48052], [77.86948, 26.67474], [77.86948, 26.67474], [80.76697, 26.52717],
                    [8.191567, 0.0], [8.191567, 0.0], [57.53074, 8.929277], [57.53074, 8.929277], [76.30083, 21.21631],
                    [76.30083, 21.21631], [87.12903, 25.42943], [87.12903, 25.42943], [93.97798, 24.47545],
                    [93.97798, 24.47545], [98.14906, 24.45528]],
     'z_velocity': [[6.156906, 0.0], [6.156906, 0.0], [41.97793, 41.12622], [41.97793, 41.12622], [54.99064, 57.09755],
                    [54.99064, 57.09755], [62.5016, 63.22052], [62.5016, 63.22052], [67.08294, 67.01094],
                    [67.08294, 67.01094], [69.85043, 69.32323], [6.560871, 0.0], [6.560871, 0.0], [43.42329, 42.21351],
                    [43.42329, 42.21351], [56.2442, 58.30221], [56.2442, 58.30221], [63.48174, 64.29683],
                    [63.48174, 64.29683], [67.69599, 67.88285], [67.69599, 67.88285], [70.21494, 70.01336],
                    [5.735697, 0.0], [5.735697, 0.0], [40.28275, 39.86841], [40.28275, 39.86841], [53.42548, 55.45014],
                    [53.42548, 55.45014], [61.00734, 61.66449], [61.00734, 61.66449], [65.80294, 65.56478],
                    [65.80294, 65.56478], [68.72351, 67.9901]],
     'i': [100, 600, 1100, 1600, 2100, 2600, 3100, 3600, 4100, 4600, 100, 600, 1100, 1600, 2100, 2600, 3100, 3600, 4100,
           4600, 100, 600, 1100, 1600, 2100, 2600, 3100, 3600, 4100, 4600]}

    xmf_param = read_xmf(f, xmf_param)
    foo = calc_xmf(xmf_param)
    print(calc_xmf(xmf_param))
    pass




