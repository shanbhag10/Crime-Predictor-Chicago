#!/usr/local/bin/python3

"""Script to find co-location patterns."""

import math
import numpy as np
import pandas as pd
import pickle
import sys

from tabulate import tabulate
from time import time

mainDF = None
featureMap = {}
candidateFeatures = []
tableInstances = []
total_num_instances = {}
count_tables = {}
colocationRules = []
coLocations = []
distThreshold = None
colocationMap = {}

currLat = None
currLong = None

tableList = []

distancePickle = None


class Table(object):
    """Datastructure to save colocation."""

    def __init__(self, colocationName, record):
        """Constructor."""
        self.prevalence = True
        self.name = colocationName
        # self.id = Table.newId()
        self.record = record  # DataFrame
        self.participation_idx = 1
        count_tables[colocationName] = len(record.index)

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


def readParams(configFile):
    """Read commandline parameters and parse the config file."""
    with open(configFile, 'r') as configFileHandle:
        print('Reading config file :{}'.format(configFile), end=', ')
        featuresFile = configFileHandle.read().strip()
        print('Done')
    return featuresFile


def mapFeatures(featuresList):
    """Map file names to Alphabet for short dictionary keys."""
    global featureMap
    global mainDF

    print('\nFeature --> Shortname')
    for num, feature in enumerate(featuresList):
        alphabet = chr(65 + num)
        featureMap[feature] = alphabet
        cnt = len(mainDF[mainDF['feature'] == feature].index)
        print('{} --> {}: {}'.format(feature, alphabet, cnt))
    print('\n')


def loadmainDF(featuresFile):
    """Generate the features map."""
    global mainDF
    global featureMap

    # Add column name
    columns = ['rowId', 'lat', 'long', 'feature']
    mainDF = pd.read_csv(featuresFile, names=columns)
    featuresList = sorted(list(set(mainDF['feature'])))

    # Map features
    mapFeatures(featuresList)

    # Map feature to Alphabet for all the records
    mainDF['feature'] = mainDF['feature'].apply(
        lambda x: featureMap[x])

    print('Total {} records'.format(len(mainDF.index)))


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

    features = [_ for _ in featureMap.values()]
    featureCount = len(features)

    for idx1 in range(featureCount):
        currFeature = features[idx1]

        # Current feature records
        cR = mainDF[mainDF['feature'] == currFeature]

        for idx2 in range(idx1 + 1, featureCount):
            # Other feature records
            otherFeature = features[idx2]
            print('Generating colocation table for {}{}'.format(currFeature,
                                                                otherFeature))
            oR = mainDF[mainDF['feature'] == otherFeature]
            copyOR = oR
            tempRowInsts = []

            start = time()
            processed = 0
            recCount = len(cR.index)

            for _, row in cR.iterrows():
                currLat, currLong = row['lat'], row['long']
                index = row['rowId']

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
                            [index, oR.iloc[idx]['rowId']])
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


def subsequences(string, n):
    """Compute the subsequnces."""
    return [string[i:i+n] for i in range(len(string)-n+1)]


def isValidCandidate(tableA, tableB, size):
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
    for i in range(0, len(prunedTables)-1):
        for j in range(i+1, len(prunedTables)):
            if isValidCandidate(prunedTables[i], prunedTables[j], size + 1):
                found_index, joinT = joinTables(prunedTables[i],
                                                prunedTables[j])
                if found_index == -1:
                    tableInstances[size].append(joinT)


def calculatePrevalence(size, prevalence_threshold):
    """Calculate Prevalence."""
    for i in range(0, len(tableInstances[size-1])):
        features = tableInstances[size-1][i].record.columns.values.tolist()
        number_of_instances = [len(np.unique(tableInstances[size-1][i].record[f].values)) for f in features]
        participation_ratios = [float(number_of_instances[index])/total_num_instances[f] for index, f in enumerate(features)]
        if tableInstances[size-1][i].name == 'IM':
            print(number_of_instances)
            print(total_num_instances)
        participation_idx = min(participation_ratios)
        tableInstances[size-1][i].set_participation_idx(participation_idx, prevalence_threshold)
        count_tables[tableInstances[size-1][i].name] = len(tableInstances[size-1][i].record.index)
        print('Table Name {} : Participation Index -> {}'.format(tableInstances[size-1][i].name, participation_idx))


def initializeColocation(prevalence_threshold):
    """Initialize Colocation."""
    global featureMap
    global colocationMap
    global distancePickle

    initial_tables_1 = []
    for feature in featureMap:
        rowIds = mainDF['rowId'][mainDF['feature'] ==
                                 featureMap[feature]].values
        total_num_instances[featureMap[feature]] = len(rowIds)
        records = pd.DataFrame(data=rowIds, columns=[feature])
        table = Table(featureMap[feature], records)
        initial_tables_1.append(table)

    tableInstances.append(initial_tables_1)
    with open(distancePickle, 'rb') as f:
        initial_tables_2 = pickle.load(f)

    tableInstances.append(initial_tables_2)
    calculatePrevalence(2, prevalence_threshold)
    # For colocation of size 2
    generateColocationRules(1)


def generateColocationRules(size):
    """Generate the co-location rules."""
    global colocationRules
    global coLocations
    for i in range(0, len(tableInstances[size])):
        if tableInstances[size][i].prevalence:
            substrings = []
            for j in range(len(tableInstances[size][i].name)):
                s = subsequences(tableInstances[size][i].name, j)
                substrings.append(s)
            flat_substrings_list = [item for sublist in substrings for item in sublist]
            flat_substrings_list = list(filter(None, flat_substrings_list))
            for sub_str in flat_substrings_list:
                if sub_str not in count_tables or count_tables[sub_str] == 0:
                    continue
                rule_name = sub_str + '->' + tableInstances[size][i].name.replace(sub_str, "")
                conditional_probability = (float)(len(tableInstances[size][i].record[list(sub_str)].drop_duplicates().index)) / count_tables[sub_str]
                if conditional_probability > 1:
                    continue
                rule = {}
                rule[rule_name] = round(conditional_probability, 3)
                colocationRules.append(rule)

            coLocations.append(tableInstances[size][i].name)


def colocationMinerAlgo(prevalence_threshold):
    """Run the Colocation Miner Algorithm."""
    initializeColocation(prevalence_threshold)
    previousColocation = True
    for k in range(3, len(featureMap)):
        if previousColocation:
            createCandidates(k-1)
            calculatePrevalence(k, prevalence_threshold)
            # print(tableInstances[k-1])
            generateColocationRules(k-1)
        else:
            break


def createQGISFiles():
    """Generate Files for QGIS."""
    for i in range(2, len(tableInstances)):
        for table in tableInstances[i]:
            rows = []
            if table.prevalence:
                features = list(table.name)
                for index, row in table.record.iterrows():
                    if index % 30 != 0:
                        continue
                    if index > 1000:
                        break
                    for f in features:
                        curRow = []
                        curRow.append(mainDF['lat'][mainDF['rowId'] == row[f]]
                                      .values[0])
                        curRow.append(mainDF['long'][mainDF['rowId'] == row[f]]
                                      .values[0])
                        curRow.append(index+1)
                        rows.append(curRow)

                df = pd.DataFrame(rows, columns=['Lat', 'Long', 'group'])
                df.to_csv('../data/output/' + table.name + '.csv')


def main():
    """Initialize everything and run the algorithm."""
    global distThreshold
    global colocationMap
    global distancePickle

    mainStart = time()

    if len(sys.argv) < 2:
        print('Please pass the parameters <CONFIG_FILE>')
        sys.exit(-1)
    configFile = sys.argv[1]

    # Value that determines the neighbor relation
    distThreshold = 0.45
    # Value that determines the prevalence index
    prevIndexThres = 0.80
    # Other configurations
    usePickle = True
    qgisFiles = True
    # Pickle file name
    distancePickle = '../data/pickle/dist45.pickle'

    print('######### CONFIGURATION #########')
    print('Distance Threshold: {}'.format(distThreshold))
    print('Prevalence Index: {}'.format(prevIndexThres))
    print('#################################')

    featuresFile = readParams(configFile)
    loadmainDF(featuresFile)

    if not usePickle:
        createColocationMap(featureMap)

        with open(distancePickle, 'wb') as pickleHandle:
            pickle.dump(colocationMap[2], pickleHandle)

    colocationMinerAlgo(prevIndexThres)
    print('Colocated Features: {}'.format(coLocations))
    print('Colocation Rules: {}'.format(colocationRules))

    print('Total time Taken {}'.format(time()-mainStart))

    if qgisFiles:
        createQGISFiles()


if __name__ == "__main__":
    main()
