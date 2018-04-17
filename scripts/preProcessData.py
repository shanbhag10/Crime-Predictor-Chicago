#!/usr/local/bin/python3

"""Script to process the raw files and Generate input files for algorithm."""

import pandas as pd
import sys
import os


def readParams(configFile):
    """Read commandline parameters and parse the config file."""
    paramList = []
    with open(configFile, 'r') as configFileHandle:
        print('Reading config file :{}'.format(configFile), end=', ')
        firstLine = True

        for line in configFileHandle:
            if(firstLine):
                outFile = line.strip()
                firstLine = False
            else:
                params = [param.replace('"', '').strip()
                        for param in line.split(',')]
                
                #featureName = os.path.basename(params[0]).split('.')[0]
                paramList.append(params)

        print('Done')
        print('{} raw files found'.format(len(paramList)))
    return outFile, paramList



def processRawData(outFileName, paramList):
    """Process the raw files based in the params."""
    
    rawDataFrame1=pd.DataFrame()
    
    for params in paramList:
        inName = params[0]
        key = params[1]
        colKey = params[2]
        lat = params[3]
        lon = params[4]
        
        print('Processing raw file: {}'.format(inName), end=', ')
        print()
        

        featureName = os.path.basename(inName).split('.')[0]
        
        rawDataFrame = pd.read_csv(inName)

        rawDataFrame.columns = [col.strip() for col in rawDataFrame.columns]
        if colKey != '' and key != '':
            rawDataFrame = rawDataFrame.loc[rawDataFrame[colKey] == key]
            featureName = key
       
        
        rawDataFrame = rawDataFrame[[lat, lon]]
        rawDataFrame.rename(columns={lat:'LATITUDE',lon:'LONGITUDE'},inplace = True)
        rawDataFrame['FEATURE'] = featureName
        rawDataFrame['INSTANCE'] = range(len(rawDataFrame1)+1,len(rawDataFrame1)+len(rawDataFrame)+1)
        

        rawDataFrame1= rawDataFrame1.append(rawDataFrame)



    rawDataFrame1 = rawDataFrame1[['INSTANCE','LATITUDE','LONGITUDE','FEATURE']]
    print(rawDataFrame1)
  
    print(outFileName)
    
    #print(a)
    rawDataFrame1.to_csv(outFileName,header=False, index=False)    
    print('Done')

    return outFileName



def generateMainConfigFile(outputFeatures, outConfig):
    """Generate the Input file for main algorithm."""
    print('Generating main config file: {}'.format(outConfig), end=', ')
    outConfigHandle = open(outConfig, 'w')
    outConfigHandle.write(outputFeatures)
    print('Done')


def main():
    """Initialize everything and run the algorithm."""
    if len(sys.argv) < 3:
        print('Please pass the parameters <CONFIG_FILE> <OUT_CONFIG>')
        sys.exit(-1)
    configFile = sys.argv[1]
    outConfig = sys.argv[2]
    outFile = readParams(configFile)[0]
    paramList = readParams(configFile)[1]
    features = processRawData(outFile,paramList)
    generateMainConfigFile(features, outConfig)


if __name__ == '__main__':
    main()



