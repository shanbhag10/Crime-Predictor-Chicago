#!/usr/local/bin/python3

"""Script to process the raw files and Generate input files for algorithm."""

import pandas as pd
import sys


def processRawData(paramList):
    """Process the raw files based in the params."""
    for params in paramList:
        inName = params[0]
        outName = params[1]
        key = params[2]
        colKey = params[3]
        lat = params[4]
        lon = params[5]
        print('Processing raw file: {}'.format(inName))

        rawDataFrame = pd.read_csv(inName)
        rawDataFrame.columns = [col.strip() for col in rawDataFrame.columns]
        if colKey != '' and key != '':
            rawDataFrame = rawDataFrame.loc[rawDataFrame[colKey] == key]
        rawDataFrame = rawDataFrame[[lat, lon]]
        rawDataFrame.to_csv(outName, header=False, index=False)


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


def generateMainConfigFile():
    """Generate the Input file for main algorithm."""


def main():
    """Initialize everything and run the algorithm."""
    if len(sys.argv) < 2:
        print('Please pass the parameters <CONFIG_FILE>')
        sys.exit(-1)
    configFile = sys.argv[1]
    paramList = readParams(configFile)
    processRawData(paramList)
    generateMainConfigFile(paramList)

if __name__ == '__main__':
    main()
