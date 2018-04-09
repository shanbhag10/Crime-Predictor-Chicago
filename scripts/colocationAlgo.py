#!/usr/local/bin/python3

"""Script to find co-location patterns."""

import math
import os
import sys


def mapFeatureFile(featuresList):
    """Map file names to Alphabet for short dictionary keys."""
    fileFeatureMap = {}
    print('Features --> Shortname')
    for num, featureFile in enumerate(featuresList):
        feature = os.path.basename(featureFile).split('.')[0]
        alphabet = chr(65 + num)
        fileFeatureMap[feature] = alphabet
        print('{} --> {}'.format(feature, alphabet))
    return fileFeatureMap


def havDistance(origin, destination):
    """Calculate the Haversine distance between two geo co-ordiantes."""
    lat1, lon1 = origin
    lat2, lon2 = destination

    lat1 = float(lat1)
    lat2 = float(lat2)
    lon1 = float(lon1)
    lon2 = float(lon2)

    radius = 3959  # miles

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d


def readParams(configFile, outputFile):
    """Read commandline parameters and parse the config file."""
    with open(configFile, 'r') as configFileHandle:
        print('Reading config file :{}'.format(configFile), end=', ')
        configData = configFileHandle.read().strip()
        featuresList = [filePath.strip() for filePath in configData.split(',')]
        print('Done')
    return featuresList


def createFeatureMap(featuresList):
    """Generate the features map."""
    featuresMap = {}
    temp = []

    for featureFile in featuresList:
        with open(featureFile, 'r') as featureFileHandle:
            for t in featureFileHandle:
                temp.append(t.rstrip(', \n'))

            tempMap = {}
            j = 0
            for line in temp:
                tempMap[j] = line
                j += 1

            featuresMap[i] = tempMap

    return featuresMap


# def createCrimeMap(featuresList):
#     """Create the crime map."""
#     featuresMap = {}
#     temp = []
#
#     for i in range(len(featuresList)):
#         tem = open(featuresList[i], 'r')
#
#         for t in tem:
#             temp.append(t.rstrip(', \n'))
#
#         tempMap = {}
#         j = 0
#         for line in temp:
#             tempMap[j] = line
#             j += 1
#
#         featuresMap[i] = tempMap
#
#     return featuresMap


def createDistanceMap(featuresMap):
    """Generate the distance map."""
    distanceMap = {}
    for k1 in featuresMap:
        for k2 in featuresMap[k1]:
            for k3 in range(k1, len(featuresMap)):
                for k4 in featuresMap[k3]:

                    t1 = featuresMap[k1][k2].split(',')
                    t2 = featuresMap[k3][k4].split(',')

                    if havDistance(t1, t2) < 1:
                        distanceMap[(k1, k2, k3, k4)] = havDistance(t1, t2)
                        print(havDistance(t1, t2))

    return distanceMap


def main():
    """Initialize everything and run the algorithm."""
    if len(sys.argv) < 3:
        print('Please pass the parameters <CONFIG_FILE> <OUTPUT_FILE>')
        sys.exit(-1)
    configFile = sys.argv[1]
    outputFile = sys.argv[2]

    featuresList = readParams(configFile, outputFile)
    fileFeatureMap = mapFeatureFile(featuresList)
    print(fileFeatureMap)
    sys.exit()
    featuresMap = createFeatureMap(params)
    distanceMap = createDistanceMap(featuresMap)
    print(distanceMap)

if __name__ == "__main__":
    main()
