import pandas as pd


def read_top_usage(top_usage):
    """
    Cleans up the stdout from the command top. Does the formatting into lines, dropping header,
    packing into a pdDataFrame, sorting cpu (descending) and dropping some columns w/ unneccessary information.
    """

    ss = top_usage.split('\r\n')
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


def run_script(ssh, paths):
    pass