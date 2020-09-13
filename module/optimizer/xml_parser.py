from pathlib import Path

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
