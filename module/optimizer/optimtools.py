import pandas as pd

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
