#!/usr/local/bin/python3

"""Script to find co-location patterns."""

import math
import os
import sys


def mapFeatureFile(featuresList):
    """Map file names to Alphabet for short dictionary keys."""
    fileFeatureMap = {}
    print('\nFeature --> Shortname')
    for num, featureFile in enumerate(featuresList):
        feature = os.path.basename(featureFile).split('.')[0]
        alphabet = chr(65 + num)
        fileFeatureMap[feature] = alphabet
        print('{} --> {}'.format(feature, alphabet))
    print('\n')
    return fileFeatureMap


def haversineDistance(origin, destination):
    """Calculate the Haversine distance between two geo co-ordiantes."""
    lat1, lon1 = map(float, origin)
    lat2, lon2 = map(float, destination)
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
        print('{} features found'.format(len(featuresList)))
    return featuresList


def createFeatureMap(featuresList, fileFeatureMap):
    """Generate the features map."""
    featuresMap = {}

    for featureFile in featuresList:
        feature = os.path.basename(featureFile).split('.')[0]
        featureRecords = {}
        print('Creating Feature map for {}'.format(feature), end=', ')
        with open(featureFile, 'r') as featureFileHandle:
            for num, record in enumerate(featureFileHandle):
                data = record.split(',')
                featureRecords[str(num + 1)] = [float(data[0]), float(data[1])]
        featuresMap[fileFeatureMap[feature]] = featureRecords
        print('{} records added'.format(num + 1))
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
    for feature1, records1 in featuresMap.items():
        print('Mapping distance for feature {}.'.format(feature1))
        print('Records left')
        recordCount = len(records1)
        for id1, coords1 in records1.items():
            dataPoint1 = feature1 + str(id1)
            distanceMap[dataPoint1] = distanceMap.get(dataPoint1, set())
            for feature2, records2 in featuresMap.items():
                for id2, coords2 in records2.items():
                    dataPoint2 = feature2 + str(id2)
                    if feature1 == feature2 and id1 == id2:
                        continue
                    elif dataPoint2 in distanceMap[dataPoint1]:
                        continue
                    else:
                        dist = haversineDistance(coords1, coords2)
                        if dist < 1:
                            distanceMap[dataPoint1].add(dataPoint2)
                            tempSet = distanceMap.get(dataPoint2, set())
                            tempSet.add(dataPoint1)
                            distanceMap[dataPoint2] = tempSet
            recordCount -= 1
            if recordCount % 500 == 0:
                print(str(recordCount))
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
    featuresMap = createFeatureMap(featuresList, fileFeatureMap)
    distanceMap = createDistanceMap(featuresMap)
    print(distanceMap)


if __name__ == "__main__":
    main()
