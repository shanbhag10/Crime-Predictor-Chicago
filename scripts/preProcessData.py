#!/usr/local/bin/python3

"""Script to process the raw files and Generate input files for algorithm."""

import pandas as pd
import sys


def processRawData(paramList):
    """Process the raw files based in the params."""
    outFiles = []
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
        outFiles.append(outName)


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


def generateMainConfigFile(outFiles, outConfig):
    """Generate the Input file for main algorithm."""
    with open(outConfig) as outConfigHandle:
        outConfigHandle.write(','.join(outFiles))


def main():
    """Initialize everything and run the algorithm."""
    if len(sys.argv) < 3:
        print('Please pass the parameters <CONFIG_FILE> <OUT_CONFIG>')
        sys.exit(-1)
    configFile = sys.argv[1]
    outConfig = sys.argv[2]
    paramList = readParams(configFile)
    outFiles = processRawData(paramList)
    generateMainConfigFile(outFiles, outConfig)

if __name__ == '__main__':
    main()
