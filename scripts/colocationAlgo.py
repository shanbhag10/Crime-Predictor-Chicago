#!/usr/local/bin/python3

"""Script to find co-location patterns."""

import math
import os
import sys
import itertools
from itertools import chain
import pandas as pd

from time import time

class Table:
    newId = itertools.count().next
    def __init__(self,colocationName,record):
        self.prevalence = True
        self.name = colocationName
        self.id = Table.newId()
        self.record = record
        self.participation_index = 1

    def set_participation_index(self, participation_index, prevalence_threshold):
        self.participation_index = participation_index
        if participation_index < prevalence_threshold:
            self.prevalence = False



candidateFeatures = []
tableInstances = []
total_num_instances = {}
colocationRules = []


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


def createDistanceMap(featuresMap, distThreshold):
    """Generate the distance map."""
    distanceMap = {}
    for feature1, records1 in featuresMap.items():
        print('Mapping distance for feature {}.'.format(feature1))
        print('Records left')
        recordCount = len(records1)
        startTime = time()
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
                        if dist < distThreshold:
                            distanceMap[dataPoint1].add(dataPoint2)
                            tempSet = distanceMap.get(dataPoint2, set())
                            tempSet.add(dataPoint1)
                            distanceMap[dataPoint2] = tempSet
            recordCount -= 1
            if recordCount % 500 == 0:
                print('{} Time taken: {}'
                      .format(recordCount, time() - startTime))
                startTime = time()
    return distanceMap



# TODO(CORE_ALGO): add the function to run the core algorithm here
def longest_common_substring(string1, string2):
    result = ""
    len1, len2 = len(string1), len(string2)
    for i in range(len1):
        match = ""
        for j in range(len2):
            if (i + j < len1 and string1[i + j] == string2[j]):
                match += string2[j]
            else:
                if (len(match) > len(result)): result = match
                match = ""
    return result





def isValidCandidate(tableA, tableB,size):
    name = tableA.name + tableB.name
    coLocationName = ''.join(set(name))
    return size == len(coLocationName)



def joinTables(tableA, tableB):
    name = tableA.name + tableB.name
    coLocationName = ''.join(sorted(set(name)))
    commonFeatures = longest_common_substring(tableA.name, tableB.name)
    records = pd.merge(tableA.records, tableB.records, how='inner', on= list(commonFeatures))
    table = Table(coLocationName, records)
    return table



def createCandidates(size):
    prunedTables = [instance for instance in tableInstances[size-1] if instance.prevalence == True]
    tableInstances.append([])
    for i in range(0,len(prunedTables)-1):
        for j in range(i+1,len(prunedTables)):
            if isValidCandidate(prunedTables[i],prunedTables[j], size + 1):
                joinT = joinTables(prunedTables[i],prunedTables[j])
                tableInstances[size].append(joinT)



def calculatePrevalence(size, prevalence_threshold):
    for i in range(0, tableInstances[size]):
        features = tableInstances[size][i].columns.values.tolist()
        number_of_instances = [len(np.unique(tableInstances[size][i][f].values)) for f in features]
        participation_ratios = [ float(number_of_instances)/total_num_instances[f] for index, f in enumerate(features)]
        participation_index = min(participation_ratios)
        tableInstances[size][i].set_particpation_index(participation_index, prevalence_threshold)
        

def initializeColocation(df):
    initial_tables_1 = []
    for feature in featuresMap:
        transactionIds = df['transaction_id'][df['feature'] == featuresMap[feature]].values
        total_num_instances[feature] = len(transactionIds)
        records = pd.DataFrame(data = transactionIds, columns= [feature])
        table = Table(feature, records)
        initial_tables_1.append(table)

    tableInstances.append(initial_tables_1)

    initial_tables_2 = []
    sorted_features = sorted(featuresMap.keys())
    for i in range(0,len(sorted_features) -1):
        for j in range(i+1, len(sorted_features)):
            transactionIds_1 = df['transaction_id'][df['feature'] == featuresMap[sorted_features[i]]].values
            transactionIds_2 = df['transaction_id'][df['feature'] == featuresMap[sorted_features[j]]].values
            records = pd.DataFrame(data = list(zip(transactionIds_1, transactionIds_2)), columns= list(zip(sorted_features[i], sorted_features[])))
            feature = sorted_features[i] + sorted_features[j]
            table = Table(feature, records)
            initial_tables_2.append(table)
    tableInstances.append(initial_tables_2)
    calculatePrevalence(2)



def generateColocationRules(size):
    for i in range(0,len(tableInstances[size])):
        if tableInstances[size][i].prevalence:
            colocationRules.append(tableInstances[size][i].name)



def colocationMinerAlgo(df, prevalence_threshold):
    initializeColocation(df)
    previousColocation = True
    for k in range(3, len(featuresMap)):
        if previousColocation:
            createCandidates(k-1)
            calculatePrevalence(k-1, prevalence_threshold)
            generateColocationRules(k-1)
        else:
            break




def main():
    """Initialize everything and run the algorithm."""
    if len(sys.argv) < 3:
        print('Please pass the parameters <CONFIG_FILE> <OUTPUT_FILE>')
        sys.exit(-1)
    configFile = sys.argv[1]
    outputFile = sys.argv[2]

    # Value that determines the neighbor relation
    distThreshold = 0.5

    featuresList = readParams(configFile, outputFile)
    fileFeatureMap = mapFeatureFile(featuresList)
    featuresMap = createFeatureMap(featuresList, fileFeatureMap)
    distanceMap = createDistanceMap(featuresMap, distThreshold)

    candidateFeatures.append(featuresMap.keys())

    # df = 
    colocationMinerAlgo(df, 0.5)
    print(featuresMap)
    print(distanceMap)


if __name__ == "__main__":
    main()
