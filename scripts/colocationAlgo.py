#!/usr/local/bin/python3

"""Script to find co-location patterns."""

import math
import os
import pandas as pd
import sys
import threading


from collections import OrderedDict
from concurrent import futures
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

class Table:
    # newId = itertools.count().next
    def __init__(self,colocationName,record):
        self.prevalence = True
        self.name = colocationName
        # self.id = Table.newId()
        self.record = record # DataFrame
        self.participation_index = 1

    def set_participation_index(self, participation_index, prevalence_threshold):
        self.participation_index = participation_index
        if participation_index < prevalence_threshold:
            self.prevalence = False


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

    for idx1 in range(featureCount):
        currFeature = features[idx1]
        print('Generating colocation table for {}*'.format(currFeature))

        # Current feature records
        cR = mainDataFrame[mainDataFrame['feature'] == currFeature]

        for idx2 in range(idx1 + 1, featureCount):
            # Other feature records
            otherFeature = features[idx2]
            oR = mainDataFrame[mainDataFrame['feature'] == otherFeature]
            copyOR = oR
            tempRowInsts = []
            for _, row in cR.iterrows():
                currLat, currLong = row['lat'], row['long']
                index = row['transaction_id']
                #print('{} {}'.format(index, len(oR.index)), end=', ')
                latUp = row['lat'] + 0.00725
                latLow = row['lat'] - 0.00725
                longUp = row['long'] + 0.00725
                longLow = row['long'] - 0.00725

                oR = oR[(oR['lat'] < latUp)]
                oR = oR[(oR['lat'] > latLow)]
                oR = oR[(oR['long'] > longLow)]
                oR = oR[(oR['lat'] > longUp)]

                #print('{}'.format(len(oR.index)))

                if len(oR.index) == 0:
                    continue
                start = time()
                destinationCoords = oR[['lat', 'long']].values.tolist()
                executor = futures.ThreadPoolExecutor(max_workers=8)
                results = executor.map(haversineDistance, destinationCoords)
                print('time taken: {}'.format(time()-start))
                for idx, res in enumerate(results):
                    if res:
                        tempRowInsts.append([index, oR.iloc[idx]['transaction_id']])
                oR = copyOR

            colocationTable = Table(currFeature + otherFeature, pd.DataFrame(tempRowInsts))
            colocationMap[2].append(colocationTable)
            # print(colocationTable.name)
            # print(colocationTable.record)

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
# def longest_common_substring(string1, string2):
#     result = ""
#     len1, len2 = len(string1), len(string2)
#     for i in range(len1):
#         match = ""
#         for j in range(len2):
#             if (i + j < len1 and string1[i + j] == string2[j]):
#                 match += string2[j]
#             else:
#                 if (len(match) > len(result)): result = match
#                 match = ""
#     return result
#
#
#
#
#
# def isValidCandidate(tableA, tableB,size):
#     name = tableA.name + tableB.name
#     coLocationName = ''.join(set(name))
#     return size == len(coLocationName)



# def joinTables(tableA, tableB):
#     name = tableA.name + tableB.name
#     coLocationName = ''.join(sorted(set(name)))
#     commonFeatures = longest_common_substring(tableA.name, tableB.name)
#     records = pd.merge(tableA.records, tableB.records, how='inner', on= list(commonFeatures))
#     table = Table(coLocationName, records)
#     return table
#
#
#
# def createCandidates(size):
#     prunedTables = [instance for instance in tableInstances[size-1] if instance.prevalence == True]
#     tableInstances.append([])
#     for i in range(0,len(prunedTables)-1):
#         for j in range(i+1,len(prunedTables)):
#             if isValidCandidate(prunedTables[i],prunedTables[j], size + 1):
#                 joinT = joinTables(prunedTables[i],prunedTables[j])
#                 tableInstances[size].append(joinT)



# def calculatePrevalence(size, prevalence_threshold):
#     for i in range(0, tableInstances[size]):
#         features = tableInstances[size][i].columns.values.tolist()
#         number_of_instances = [len(np.unique(tableInstances[size][i][f].values)) for f in features]
#         participation_ratios = [ float(number_of_instances)/total_num_instances[f] for index, f in enumerate(features)]
#         participation_index = min(participation_ratios)
#         tableInstances[size][i].set_particpation_index(participation_index, prevalence_threshold)
#
#
# def initializeColocation(df):
#     initial_tables_1 = []
#     for feature in featuresMap:
#         transactionIds = df['transaction_id'][df['feature'] == featuresMap[feature]].values
#         total_num_instances[feature] = len(transactionIds)
#         records = pd.DataFrame(data = transactionIds, columns= [feature])
#         table = Table(feature, records)
#         initial_tables_1.append(table)
#
#     tableInstances.append(initial_tables_1)
#
#     initial_tables_2 = []
#     sorted_features = sorted(featuresMap.keys())
#     for i in range(0,len(sorted_features) -1):
#         for j in range(i+1, len(sorted_features)):
#             transactionIds_1 = df['transaction_id'][df['feature'] == featuresMap[sorted_features[i]]].values
#             transactionIds_2 = df['transaction_id'][df['feature'] == featuresMap[sorted_features[j]]].values
#             records = pd.DataFrame(data = list(zip(transactionIds_1, transactionIds_2)), columns= list(zip(sorted_features[i], sorted_features[])))
#             feature = sorted_features[i] + sorted_features[j]
#             table = Table(feature, records)
#             initial_tables_2.append(table)
#     tableInstances.append(initial_tables_2)
#     calculatePrevalence(2)
#
#
#
# def generateColocationRules(size):
#     for i in range(0,len(tableInstances[size])):
#         if tableInstances[size][i].prevalence:
#             colocationRules.append(tableInstances[size][i].name)


#
# def colocationMinerAlgo(df, prevalence_threshold):
#     initializeColocation(df)
#     previousColocation = True
#     for k in range(3, len(featuresMap)):
#         if previousColocation:
#             createCandidates(k-1)
#             calculatePrevalence(k-1, prevalence_threshold)
#             generateColocationRules(k-1)
#         else:
#             break




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
    print(colocationMap)
    # candidateFeatures.append(featuresMap.keys())

    # df =
    #colocationMinerAlgo(df, 0.5)
    #print(featuresMap)
    #print(distanceMap)


if __name__ == "__main__":
    main()
