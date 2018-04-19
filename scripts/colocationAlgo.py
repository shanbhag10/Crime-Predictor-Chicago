#!/usr/local/bin/python3

"""Script to find co-location patterns."""

import math
import os
import pandas as pd
import sys
import threading
import numpy as np
import pickle


from collections import OrderedDict
from concurrent import futures
from time import time
from tabulate import tabulate
from difflib import SequenceMatcher


mainDataFrame = None
fileFeatureMap = {}
candidateFeatures = []
tableInstances = []
total_num_instances = {}
colocationRules = []
distThreshold = None
colocationMap = {}

currLat = None
currLong = None

tableList = []


class Table:
    # newId = itertools.count().next
    def __init__(self, colocationName, record):
        self.prevalence = True
        self.name = colocationName
        # self.id = Table.newId()
        self.record = record  # DataFrame
        self.participation_index = 1

    def set_participation_index(self, participation_index, prevalence_threshold):
        self.participation_index = participation_index
        if participation_index < prevalence_threshold:
            self.prevalence = False

    def __str__(self):
        return 'Name :{}, Record: {}'.format(self.name, tabulate(self.record, headers='keys', tablefmt='psql'))
        


    __repr__ = __str__




def readParams(configFile, outputFile):
    """Read commandline parameters and parse the config file."""
    with open(configFile, 'r') as configFileHandle:
        print('Reading config file :{}'.format(configFile), end=', ')
        featuresFile = configFileHandle.read().strip()
        print('Done')
    return featuresFile


def mapFeatures(featuresList):
    """Map file names to Alphabet for short dictionary keys."""
    global fileFeatureMap
    print('\nFeature --> Shortname')
    for num, feature in enumerate(featuresList):
        alphabet = chr(65 + num)
        fileFeatureMap[feature] = alphabet
        print('{} --> {}'.format(feature, alphabet))
    print('\n')


def loadMainDataFrame(featuresFile):
    """Generate the features map."""
    global mainDataFrame
    global fileFeatureMap

    # Add column name
    columns = ['transaction_id', 'lat', 'long', 'feature']
    #mainDataFrame = pd.read_csv(featuresFile, index_col=0, names=columns)
    mainDataFrame = pd.read_csv(featuresFile, names=columns)
    featuresList = set(mainDataFrame['feature'])

    # Map features
    mapFeatures(featuresList)

    # Map feature to Alphabet for all the records
    mainDataFrame['feature'] = mainDataFrame['feature'].apply(
        lambda x: fileFeatureMap[x])

    print('Total {} records'.format(len(mainDataFrame.index)))


# def haversineDistance(origin, destination):
def haversineDistance(destination):
    """Calculate the Haversine distance between two geo co-ordiantes."""
    # lat1, lon1 = map(float, origin)
    global currLat
    global currLong
    lat1, lon1 = currLat, currLong
    lat2, lon2 = map(float, destination)
    #print(lat1, lon1, lat2, lon2)
    radius = 3959  # miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    if d < distThreshold:
        return True
    else:
        return False


def createColocationMap(featuresMap):
    """Generate the distance map."""
    global currLat
    global currLong
    global colocationMap

    colocationMap[2] = []

    features = [_ for _ in fileFeatureMap.values()]
    featureCount = len(features)

    executor = futures.ThreadPoolExecutor(max_workers=20)

    for idx1 in range(featureCount):
        currFeature = features[idx1]

        # Current feature records
        cR = mainDataFrame[mainDataFrame['feature'] == currFeature]

        for idx2 in range(idx1 + 1, featureCount):
            # Other feature records
            otherFeature = features[idx2]
            print('Generating colocation table for {}{}'.format(currFeature, otherFeature))
            oR = mainDataFrame[mainDataFrame['feature'] == otherFeature]
            copyOR = oR
            tempRowInsts = []

            start = time()
            processed = 0
            recCount = len(cR.index)

            for _, row in cR.iterrows():
                currLat, currLong = row['lat'], row['long']
                index = row['transaction_id']
                # print('{} {}'.format(index, len(oR.index)), end=', ')
                latUp = row['lat'] + 0.00725
                latLow = row['lat'] - 0.00725
                longUp = row['long'] + 0.00725
                longLow = row['long'] - 0.00725

                oR = oR[(oR['lat'] < latUp)]
                oR = oR[(oR['lat'] > latLow)]
                oR = oR[(oR['long'] > longLow)]
                oR = oR[(oR['lat'] > longUp)]

                # print('{}'.format(len(oR.index)))

                if len(oR.index) == 0:
                    processed += 1
                    if processed % 500 == 0 or processed == recCount:
                        end = time() - start
                        print('{} {} {}'.format(processed, end,
                                                   recCount - processed))
                        start = time()
                    continue

                destinationCoords = oR[['lat', 'long']].values.tolist()
                results = executor.map(haversineDistance, destinationCoords)

                for idx, res in enumerate(results):
                    if res:
                        tempRowInsts.append(
                            [index, oR.iloc[idx]['transaction_id']])
                oR = copyOR

                processed += 1
                if processed % 500 == 0 or processed == recCount:
                    end = time() - start
                    print('{} {} {}'.format(processed, end,
                                               recCount - processed))
                    start = time()

            colocationTable = Table(
                currFeature + otherFeature, pd.DataFrame(tempRowInsts, columns = [currFeature, otherFeature]))
            colocationMap[2].append(colocationTable)

        # records = mainDataFrame[(mainDataFrame['feature'] != features[idx1]) & (mainDataFrame['lat'] = )]
        # for records in range(idx1 + 1, featureCount):

    # distanceMap = {}
    # for feature1, records1 in featuresMap.items():
    #     print('Mapping distance for feature {}.'.format(feature1))
    #     print('Records left')
    #     recordCount = len(records1)
    #     startTime = time()
    #     for id1, coords1 in records1.items():
    #         dataPoint1 = feature1 + str(id1)
    #         distanceMap[dataPoint1] = distanceMap.get(dataPoint1, set())
    #         for feature2, records2 in featuresMap.items():
    #             for id2, coords2 in records2.items():
    #                 dataPoint2 = feature2 + str(id2)
    #                 if feature1 == feature2 and id1 == id2:
    #                     continue
    #                 elif dataPoint2 in distanceMap[dataPoint1]:
    #                     continue
    #                 else:
    #                     dist = haversineDistance(coords1, coords2)
    #                     if dist < distThreshold:
    #                         distanceMap[dataPoint1].add(dataPoint2)
    #                         tempSet = distanceMap.get(dataPoint2, set())
    #                         tempSet.add(dataPoint1)
    #                         distanceMap[dataPoint2] = tempSet
    #         recordCount -= 1
    #         if recordCount % 500 == 0:
    #             print('{} Time taken: {}'
    #                   .format(recordCount, time() - startTime))
    #             startTime = time()
    # return distanceMap


# # TODO(CORE_ALGO): add the function to run the core algorithm here
def longest_common_substring(string1, string2): 
    # result = ""
    # len1, len2 = len(string1), len(string2)
    # for i in range(len1):
    #     match = ""
    #     for j in range(len2):
    #         if (i + j < len1 and string1[i + j] == string2[j]):
    #             match += string2[j]
    #         else:
    #             if (len(match) > len(result)): result = match
    #             match = ""
    # return result
    m = len(string1)
    n = len(string2)

    L = [[0 for x in range(n+1)] for x in range(m+1)]
 
    # Following steps build L[m+1][n+1] in bottom up fashion. Note
    # that L[i][j] contains length of LCS of X[0..i-1] and Y[0..j-1] 
    for i in range(m+1):
        for j in range(n+1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif string1[i-1] == string2[j-1]:
                L[i][j] = L[i-1][j-1] + 1
            else:
                L[i][j] = max(L[i-1][j], L[i][j-1])
 
    # Following code is used to print LCS
    index = L[m][n]
 
    # Create a character array to store the lcs string
    lcs = [""] * (index+1)
    lcs[index] = ""
 
    # Start from the right-most-bottom-most corner and
    # one by one store characters in lcs[]
    i = m
    j = n
    while i > 0 and j > 0:
 
        # If current character in X[] and Y are same, then
        # current character is part of LCS
        if string1[i-1] == string2[j-1]:
            lcs[index-1] = string1[i-1]
            i-=1
            j-=1
            index-=1
 
        # If not same, then find the larger of two and
        # go in the direction of larger value
        elif L[i-1][j] > L[i][j-1]:
            i-=1
        else:
            j-=1
 
    return "".join(lcs)





def isValidCandidate(tableA, tableB,size):
    name = tableA.name + tableB.name
    coLocationName = ''.join(set(name))
    return size == len(coLocationName)


def joinTables(tableA, tableB):
    name = tableA.name + tableB.name
    coLocationName = ''.join(sorted(set(name)))
    print('Joining {} and {} : New Colocation:{}'.format(tableA.name, tableB.name, coLocationName))
    commonFeatures = longest_common_substring(tableA.name, tableB.name)
    if len(commonFeatures) > 1:
        commonFeatures = list(commonFeatures)
    print(commonFeatures)
    records = pd.merge(tableA.record, tableB.record, how='inner', on= commonFeatures)
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
    for i in range(0, len(tableInstances[size-1])):
        features = tableInstances[size-1][i].record.columns.values.tolist()
        number_of_instances = [len(np.unique(tableInstances[size-1][i].record[f].values)) for f in features]
        participation_ratios = [ float(number_of_instances[index])/total_num_instances[f] for index, f in enumerate(features)]
        participation_index = min(participation_ratios)
        tableInstances[size-1][i].set_participation_index(participation_index, prevalence_threshold)
        print('Table Name {} : Participation Index -> {}'.format(tableInstances[size-1][i].name, participation_index))


def initializeColocation(prevalence_threshold):
    global fileFeatureMap
    global colocationMap
    initial_tables_1 = []
    for feature in fileFeatureMap:
        transactionIds = mainDataFrame['transaction_id'][mainDataFrame['feature'] == fileFeatureMap[feature]].values
        total_num_instances[fileFeatureMap[feature]] = len(transactionIds)
        records = pd.DataFrame(data = transactionIds, columns= [feature])
        table = Table(feature, records)
        initial_tables_1.append(table)

    tableInstances.append(initial_tables_1)
    print('Total Instances per feature : {}'.format(total_num_instances))
    with open('entry.pickle', 'rb') as f:
        initial_tables_2 = pickle.load(f)    

     #initial_tables_2 = colocationMap[2]
    # sorted_features = sorted(featuresMap.keys())
    # for i in range(0,len(sorted_features) -1):
    #     for j in range(i+1, len(sorted_features)):
    #         transactionIds_1 = df['transaction_id'][df['feature'] == featuresMap[sorted_features[i]]].values
    #         transactionIds_2 = df['transaction_id'][df['feature'] == featuresMap[sorted_features[j]]].values
    #         records = pd.DataFrame(data = list(zip(transactionIds_1, transactionIds_2)), columns= list(zip(sorted_features[i], sorted_features[])))
    #         feature = sorted_features[i] + sorted_features[j]
    #         table = Table(feature, records)
    #         initial_tables_2.append(table)
    tableInstances.append(initial_tables_2)
    calculatePrevalence(2,prevalence_threshold)



def generateColocationRules(size):
    global colocationRules
    for i in range(0,len(tableInstances[size])):
        if tableInstances[size][i].prevalence:
            colocationRules.append(tableInstances[size][i].name)



def colocationMinerAlgo(prevalence_threshold):
    initializeColocation(prevalence_threshold)
    previousColocation = True
    for k in range(3, len(fileFeatureMap)):
        if previousColocation:
            createCandidates(k-1)
            calculatePrevalence(k, prevalence_threshold)
            #print(tableInstances[k-1])
            generateColocationRules(k-1)
        else:
            break


def main():
    """Initialize everything and run the algorithm."""
    global distThreshold
    global colocationMap

    if len(sys.argv) < 3:
        print('Please pass the parameters <CONFIG_FILE> <OUTPUT_FILE>')
        sys.exit(-1)
    configFile = sys.argv[1]
    outputFile = sys.argv[2]

    # Value that determines the neighbor relation
    distThreshold = 0.5

    featuresFile = readParams(configFile, outputFile)
    loadMainDataFrame(featuresFile)
    createColocationMap(fileFeatureMap)
    #print(colocationMap)
    # candidateFeatures.append(featuresMap.keys())

    # df =
    with open('entry.pickle', 'wb') as f:
        pickle.dump(colocationMap[2], f) 
    colocationMinerAlgo(0.5)
    print(colocationRules)
    # print(featuresMap)
    # print(distanceMap)


if __name__ == "__main__":
    main()
