#!/usr/local/bin/python3

"""Script to find co-location patterns."""

import math
import numpy as np
import pandas as pd
import pickle
import sys

from concurrent import futures
from tabulate import tabulate
from time import time

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


class Table(object):
    """Datastructure to save colocation."""

    def __init__(self, colocationName, record):
        """Constructor."""
        self.prevalence = True
        self.name = colocationName
        # self.id = Table.newId()
        self.record = record  # DataFrame
        self.participation_idx = 1

    def set_participation_idx(self, participation_idx, prevalence_threshold):
        """Set the participation Index."""
        self.participation_idx = participation_idx
        if participation_idx < prevalence_threshold:
            self.prevalence = False

    def __str__(self):
        """Represent the object in string."""
        return 'Name :{}, Record: {}'.format(self.name,
                                             tabulate(self.record,
                                                      headers='keys',
                                                      tablefmt='psql'))

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
    global mainDataFrame

    print('\nFeature --> Shortname')
    for num, feature in enumerate(featuresList):
        alphabet = chr(65 + num)
        fileFeatureMap[feature] = alphabet
        cnt = len(mainDataFrame[mainDataFrame['feature'] == feature].index)
        print('{} --> {}: {}'.format(feature, alphabet, cnt))
    print('\n')


def loadMainDataFrame(featuresFile):
    """Generate the features map."""
    global mainDataFrame
    global fileFeatureMap

    # Add column name
    columns = ['transaction_id', 'lat', 'long', 'feature']
    mainDataFrame = pd.read_csv(featuresFile, names=columns)
    featuresList = sorted(list(set(mainDataFrame['feature'])))

    # Map features
    mapFeatures(featuresList)

    # Map feature to Alphabet for all the records
    mainDataFrame['feature'] = mainDataFrame['feature'].apply(
        lambda x: fileFeatureMap[x])

    print('Total {} records'.format(len(mainDataFrame.index)))


# def haversineDistance(origin, destination):
def haversineDistance(destination):
    """Calculate the Haversine distance between two geo co-ordiantes."""
    global currLat
    global currLong
    lat1, lon1 = currLat, currLong
    lat2, lon2 = map(float, destination)
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

    for idx1 in range(featureCount):
        currFeature = features[idx1]

        # Current feature records
        cR = mainDataFrame[mainDataFrame['feature'] == currFeature]

        for idx2 in range(idx1 + 1, featureCount):
            # Other feature records
            otherFeature = features[idx2]
            print('Generating colocation table for {}{}'.format(currFeature,
                                                                otherFeature))
            oR = mainDataFrame[mainDataFrame['feature'] == otherFeature]
            copyOR = oR
            tempRowInsts = []

            start = time()
            processed = 0
            recCount = len(cR.index)

            for _, row in cR.iterrows():
                currLat, currLong = row['lat'], row['long']
                index = row['transaction_id']

                latUp = row['lat'] + 0.00725
                latLow = row['lat'] - 0.00725
                longUp = row['long'] + 0.00725
                longLow = row['long'] - 0.00725

                oR = oR[(oR['lat'] < latUp)]
                oR = oR[(oR['lat'] > latLow)]
                oR = oR[(oR['long'] > longLow)]
                oR = oR[(oR['lat'] > longUp)]

                if len(oR.index) == 0:
                    processed += 1
                    if processed % 500 == 0 or processed == recCount:
                        end = time() - start
                        print('{} {} {}'.format(processed, end,
                                                recCount - processed))
                        start = time()
                    continue

                destinationCoords = oR[['lat', 'long']].values.tolist()
                results = []
                for coords in destinationCoords:
                    results.append(haversineDistance(coords))

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

            colocationTable = Table(currFeature + otherFeature,
                                    pd.DataFrame(tempRowInsts,
                                                 columns=[currFeature,
                                                          otherFeature]))
            colocationMap[2].append(colocationTable)


def longest_common_substring(string1, string2):
    """Find the common columns between two colocation table."""
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
            i -= 1
            j -= 1
            index -= 1

        # If not same, then find the larger of two and
        # go in the direction of larger value
        elif L[i-1][j] > L[i][j-1]:
            i -= 1
        else:
            j -= 1

    return "".join(lcs)


def isValidCandidate(tableA, tableB,size):
    """Check if by merging two colocation tables we can create new."""
    name = tableA.name + tableB.name
    coLocationName = ''.join(set(name))
    return size == len(coLocationName)


def joinTables(tableA, tableB):
    """Join tables and their common records."""
    name = tableA.name + tableB.name
    coLocationName = ''.join(sorted(set(name)))
    print('Joining {} and {} : New Colocation:{}'.format(tableA.name,
                                                         tableB.name,
                                                         coLocationName))
    commonFeatures = longest_common_substring(tableA.name, tableB.name)
    if len(commonFeatures) > 1:
        commonFeatures = list(commonFeatures)
    print(commonFeatures)
    records = pd.merge(tableA.record, tableB.record, how='inner',
                       on=commonFeatures)

    table = type('Table', (object,), {})()
    found_index = -1
    if len(tableInstances[len(coLocationName)-1]) > 0:
        for i in range(len(tableInstances[len(coLocationName)-1])):
            if tableInstances[len(coLocationName)-1][i].name == coLocationName:
                found_index = i
                break

    print('Found Index{}'.format(found_index))
    if found_index > -1:
        table = tableInstances[len(coLocationName)-1][i]
        table.record.append(records, ignore_index=True)
    else:
        table = Table(coLocationName, records)

    return found_index, table


def createCandidates(size):
    """Run through the pruned tables and create candidates."""
    prunedTables = []
    for instance in tableInstances[size-1]:
        if instance.prevalence:
            prunedTables.append(instance)
    tableInstances.append([])
    for i in range(0,len(prunedTables)-1):
        for j in range(i+1,len(prunedTables)):
            if isValidCandidate(prunedTables[i],prunedTables[j], size + 1):
                found_index, joinT = joinTables(prunedTables[i],
                                                prunedTables[j])
                if found_index == -1:
                    tableInstances[size].append(joinT)


def calculatePrevalence(size, prevalence_threshold):
    """Calculate Prevalence."""
    for i in range(0, len(tableInstances[size-1])):
        features = tableInstances[size-1][i].record.columns.values.tolist()
        number_of_instances = [len(np.unique(tableInstances[size-1][i].record[f].values)) for f in features]
        participation_ratios = [ float(number_of_instances[index])/total_num_instances[f] for index, f in enumerate(features)]
        participation_idx = min(participation_ratios)
        tableInstances[size-1][i].set_participation_idx(participation_idx, prevalence_threshold)
        print('Table Name {} : Participation Index -> {}'.format(tableInstances[size-1][i].name, participation_idx))


def initializeColocation(prevalence_threshold):
    """Initialize Colocation."""
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
    with open('entry.pickle', 'rb') as f:
        initial_tables_2 = pickle.load(f)

    tableInstances.append(initial_tables_2)
    calculatePrevalence(2,prevalence_threshold)
    generateColocationRules(1)


def generateColocationRules(size):
    """Generate the co-location rules."""
    global colocationRules
    for i in range(0,len(tableInstances[size])):
        if tableInstances[size][i].prevalence:
            colocationRules.append(tableInstances[size][i].name)


def colocationMinerAlgo(prevalence_threshold):
    """Run the Colocation Miner Algorithm."""
    initializeColocation(prevalence_threshold)
    previousColocation = True
    for k in range(3, len(fileFeatureMap)):
        if previousColocation:
            createCandidates(k-1)
            calculatePrevalence(k, prevalence_threshold)
            # print(tableInstances[k-1])
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
    #createColocationMap(fileFeatureMap)

    # with open('entry.pickle', 'wb') as pickleHandle:
    #     pickle.dump(colocationMap[2], pickleHandle)
    colocationMinerAlgo(0.5)
    print(colocationRules)


    
    for i in range(2, len(tableInstances)):
        for table in tableInstances[i]:
            rows = []
            if table.prevalence:
                features = list(table.name)
                for index, row in table.record.iterrows():
                    if index > 10:
                        break
                    for f in features:
                        current_row = []
                        current_row.append(mainDataFrame['lat'][mainDataFrame['transaction_id'] == row[f]].values[0])
                        current_row.append(mainDataFrame['long'][mainDataFrame['transaction_id'] == row[f]].values[0])
                        current_row.append(index+1)
                        rows.append(current_row)

                df = pd.DataFrame(rows, columns= ['Lat','Long', 'group'])
                df.to_csv('../data/output/'+ table.name+'.csv')


if __name__ == "__main__":
    main()
