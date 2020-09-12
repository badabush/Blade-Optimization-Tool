# https://stackoverflow.com/questions/2148119/how-to-convert-an-xml-string-to-a-dictionary

import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
import xmltodict
import time


def parse_xml(file):
    """
    Opens a xmf/xml file and returns it as a dict.
    """
    ds = {}
    try:
        with open(file) as fd:

            doc = xmltodict.parse(fd.read())
        #
        #
        # # outlet = xmldict['Station']['MassFlow']['float'][0]
        # # inlet = xmldict['Station']['MassFlow']['float'][1]
        # ds['outlet'] = doc['Computation']['MassFlow'][1]['float']['#text']
        # ds['inlet'] = doc['Computation']['MassFlow'][0]['float']['#text']
        return ds

    except FileNotFoundError:
        ds['outlet'] = 0
        ds['inlet'] = 0
        return ds


def read_by_token(fileobj):
    for line in fileobj:
        ds = []
        for token in line.split():
            ds.append(token)
        yield ds


def parse_res(file, idx):
    try:
        i = idx
        with open(file,"r") as f:
        # f = open(file,"r")
            tokenized = read_by_token(f)

            # #reads first two seperately
            # first_token = next(tokenized)
            # second_token = next(tokenized)
            ds = {}
            for token in tokenized:
                if token[0].isdigit() and len(token) > 1:
                    if int(token[0]) <= idx:
                        continue
                    ds[token[0]] = token
                    i = int(token[0])
                    print(token)
                    # f.close()
            # f.close()
            return ds, i
    except FileNotFoundError:
        print("File not found, waiting for process to start.")


if __name__ in "__main__":
    file = Path("//130.149.110.81/liang/Tandem_Opti/parent_V3/parent_V3_brustinzidenz/parent_V3_brustinzidenz.xmf")
    file2 = Path("//130.149.110.81/liang/Tandem_Opti/parent_V3/parent_V3_brustinzidenz/copyres.res")
    foo = parse_res(file2, 419)
    0
    # parse_xml(file)
