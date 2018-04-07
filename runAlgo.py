import sys
import math


def havDistance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination

    lat1 = float(lat1)
    lat2 = float(lat2)
    lon1 = float(lon1)
    lon2 = float(lon2)

    radius = 3959 #miles

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d


def readParams(ipfName,opfName):
	ipfile = open(ipfName, 'r')
	featuresList=[]
	for line in ipfile:
		temp = line.split()
		for i in temp:
			featuresList.append(i.rstrip(','))
	return featuresList


def createFeatureMap(featuresList):
	featuresMap = {}
	temp = []
	
	for i in range(len(featuresList)):
		tem = open(featuresList[i],'r')

		for t in tem:
			temp.append(t.rstrip(', \n'))

		tempMap = {}
		j=0;
		for line in temp:
			tempMap[j]=line
			j+=1

		featuresMap[i] = tempMap
		

	return featuresMap

'''
def createCrimeMap(featuresList):
	featuresMap = {}
	temp = []
	
	for i in range(len(featuresList)):
		tem = open(featuresList[i],'r')

		for t in tem:
			temp.append(t.rstrip(', \n'))

		tempMap = {}
		j=0;
		for line in temp:
			tempMap[j]=line
			j+=1

		featuresMap[i] = tempMap
		

	return featuresMap
'''

def createDistanceMap(featuresMap):

	distanceMap = {}
	for k1 in featuresMap:
		for k2 in featuresMap[k1]:
			for k3 in range(k1,len(featuresMap)):
				for k4 in featuresMap[k3]:
					
					t1 = featuresMap[k1][k2].split(',')
					t2 = featuresMap[k3][k4].split(',')
					

					if havDistance(t1,t2)<1:
						distanceMap[(k1,k2,k3,k4)] = havDistance(t1,t2)
						print(havDistance(t1,t2))

	return distanceMap


if __name__ == "__main__":
	createDistanceMap(createFeatureMap(readParams(sys.argv[1], sys.argv[2])))
