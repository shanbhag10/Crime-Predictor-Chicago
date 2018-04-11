#!/usr/local/bin/python3

"""Script to process the raw files and Generate input files for algorithm."""

import math
import numpy as np
import os
import pandas as pd
import sys

os.chdir("/Users/powerparky/Desktop/CSC591/pj")
cfname = 'homicide_config.csv'


def processrawdata():

    # read in config file
    def readparam(cfname):
        df = pd.read_csv(cfname, header=None)
        return df

    config = readparam(cfname)
    print(config)

    inname = config[0][0]
    outname = config[1][0]
    key = config[2][0]
    colkey = config[3][0]
    lat = config[4][0]
    lon = config[5][0]
    print(inname, outname, key, colkey, lat, lon)

    inputfile = readparam(inname)

    # flat the 2 dimensial list into 1 dimension.
    def flat(l):
        for k in l:
            if not isinstance(k, (list, tuple)):
                yield k
            else:
                yield from flat(k)

    # transfer DateFrame into List
    def DFtoList(df):
        list1 = np.array(df)
        list2 = list1.tolist()
        df_list = list(flat(list2))
        return df_list

    label_list = DFtoList(inputfile[0:1])
    print(label_list)

    # check if there are key and colkey
    if isinstance(key, str) or not math.isnan(key):
        search_region = label_list.index(colkey)
        tmp = inputfile[inputfile[search_region] == key]
    else:
        tmp = inputfile[1:]

    print(tmp)

    y = label_list.index(lat)
    x = label_list.index(lon)
    output_lat = tmp[y]
    output_lon = tmp[x]
    output = pd.DataFrame([output_lat, output_lon])
    output = output.T

    output.to_csv(outname, index=False, sep=',', header=None)


def readParams(configFile):
    """Read commandline parameters and parse the config file."""
    paramList = []
    with open(configFile, 'r') as configFileHandle:
        print('Reading config file :{}'.format(configFile), end=', ')
        for line in configFileHandle:
            configData = line.strip().split(',')
            paramList.append(configData)
        print('Done')
        print('{} raw files found'.format(len(paramList)))
    return paramList


def main():
    """Initialize everything and run the algorithm."""
    if len(sys.argv) < 2:
        print('Please pass the parameters <CONFIG_FILE>')
        sys.exit(-1)
    configFile = sys.argv[1]
    paramList = readParams(configFile)

if __name__ == '__main__':
    main()
    processrawdata()
