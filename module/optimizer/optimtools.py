import pandas as pd
from pathlib import Path
import xmltodict
import time

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
    Worker thread to read new lines from res. Only queues relevant lines. Breaks loop when kill==True
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
        # break

def read_xmf(file, param):

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
    y_vel = np.array(ds['y_velocity'])
    z_vel = np.array(ds['z_velocity'])
    p_stat = np.array(ds['static_pressure'])
    p_atot = np.array(ds['abs_total_pressure'])
    # beta = np.arcsin(y_vel/z_vel)
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


if __name__ == "__main__":
    f = "//130.149.110.81/liang/Tandem_Opti/parent_V3/parent_V3_brustinzidenz/parent_V3_brustinzidenz.xmf"
    # init XMF dict
    xmf_param = {}  # [['Inlet', Outlet'], ...]
    xmf_param['abs_total_pressure'] = []
    xmf_param['static_pressure'] = []
    xmf_param['y_velocity'] = []
    xmf_param['z_velocity'] = []

    read_xmf(f, xmf_param)