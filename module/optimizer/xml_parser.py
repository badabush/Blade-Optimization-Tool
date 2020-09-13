# https://stackoverflow.com/questions/2148119/how-to-convert-an-xml-string-to-a-dictionary

import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
import xmltodict
import time
import queue

def read_by_token(fileobj):
    for line in fileobj:
        ds = []
        for token in line.split():
            ds.append(token)
        yield ds


def parse_res(file, q, kill):
    fp = open(file, 'r')
    while True:
        tokenized = read_by_token(fp)
        for token in tokenized:
            if token[0].isdigit() and len(token) > 1:
                q.put(token)

        # break loop when kill==True
        if kill:
            break


if __name__ in "__main__":
    file = Path("//130.149.110.81/liang/Tandem_Opti/parent_V3/parent_V3_brustinzidenz/parent_V3_brustinzidenz.xmf")
    file2 = Path("//130.149.110.81/liang/Tandem_Opti/parent_V3/parent_V3_brustinzidenz/copyres.res")
