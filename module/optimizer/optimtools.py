import pandas as pd
from pathlib import Path

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
    Reads lines, drops everything except tokens (str, values, etc.) and appends to a list. Yields list.
    """
    for line in fileobj:
        ds = []
        for token in line.split():
            ds.append(token)
        yield ds


def parse_res(file, q, kill):
    """
    Worker thread to read new lines from res. Only queues relevant lines. Breaks loop when kill==True
    """
    fp = open(file, 'r')
    while True:
        tokenized = read_by_token(fp)
        for token in tokenized:
            if token[0].isdigit() and len(token) > 1:
                q.put(token)

        # break loop when kill==True
        if kill:
            break


def cleanpaths(paths):
    """
    Cleans up input paths for usage in generate_script and optimhandle.
    """

    path_list = []
    for key, path in paths.items():
        if path[0] == "/" and path[1] == "/":
            path = path[1:]
        path = Path(path)
        path_list.append(path.parts)

    # dict entry for every file/folder path.
    paths['dir_raw'] = paths['dir']
    if paths['dir'][0] == "/" and paths['dir'][1] == "/":
        paths['dir'] = paths['dir'][1:]
    paths['dir'] = Path(paths['dir'])
    paths['dir'] = paths['dir'].parts

    paths['usr_folder'] = paths['dir'][-2]
    paths['proj_folder'] = paths['dir'][-1]
    paths['iec'] = path_list[1][-2] + '/' + path_list[1][-1]  # iec file
    paths['igg'] = path_list[2][-1]  # igg file
    paths['run'] = path_list[3][-3] + '/' + path_list[3][-2] + '/' + path_list[3][-1]  # run file
    paths['res'] = paths['dir_raw'] + '/' + path_list[3][-3] + '/' + path_list[3][-2] + '/' + path_list[3][-1][:-3] + 'res'  # res file

    return paths
