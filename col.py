import math
import pandas as pd
'''
def haversine(point1, point2):
    
    lat1, lon1 = point1
    lat2, lon2 = point2
    radius = 3959 

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d



def support(coord1,coord2,radius):

	total = 0
	near=0
	qualified = []

	for a in coord1:
		for b in coord2:
			dist = haversine(a,b)
			total+=1
			if(dist<radius):
				near+=1	
				qualified.append((a,b))

	support = near/total


	print()
	print('Support :  ',support)
	print()
	print('Near :  ',near)
	print()
	print('Total :  ',total)
	print()
	#print('qualified : ',coords)
	return support,qualified



def support1(coordlist,coord1,radius):

	total = 0
	near=0
	qualified = []
	

	for a in coord1:
		close = 0
		for b in coordlist:
			for c in b:
				#print(c)
				dist = haversine(a,c)
				total+=1
				if(dist<radius):
					close+=1
					break
		
		if(close):
			qualified.append((a,b))
			near+=1			

	support = near/total


	print()
	print('Support :  ',support)
	print()
	print('Near :  ',near)
	print()
	print('Total :  ',total)
	print()
	#print('qualified : ',coords)
	return support,qualified



def make_rule(sup):
	if sup>0.15:
		return True
	else:
		return False


police_station_file = open('police_station_clean.csv','r')

police_coord = []

for line in police_station_file:
    police_station_name, police_station_description, police_station_address, police_station_zip, police_station_lat, police_station_long = line.split(',')
    police_station_long = police_station_long.rstrip('\n')
    police_coord.append((police_station_lat, police_station_long))

#print(police_coord)
'''

rules = []

clist = []


def drange(start, stop, step):
    while start < stop:
            yield start
            start += step


arson_df = pd.read_csv('arson.csv',names=['Date','Desc','Lat', 'Long','Loc','Block'],skiprows=1)
arson_coord = arson_df[['Lat','Long']].values


#print(arson_coord)


######### POLICE ST ########
police_station_df = pd.read_csv('police_overlap.csv',names=['UID', 'Name', 'Desc', 'Zip', 'Lat', 'Long'],skiprows=1)
police_coord = police_station_df[['Lat','Long']].values.tolist()

'''
clist.append(police_coord)

print()
print('**** POLICE STATION ****')
arson_police_support,arson_police_near_coords = support(police_coord,arson_coord,2)

if(make_rule(arson_police_support)):
	rules.append("Police Station -> Arson")

'''
######### BARS ###########
bars_df = pd.read_csv('bars_overlap.csv',names=['a','b','c','d', 'e', 'f', 'g', 'Lat', 'Long'],skiprows=1)
bars_coord = bars_df[['Lat','Long']].values.tolist()

'''clist.append(bars_coord)


#print(clist)

print()

print('**** BARS ****')
arson_bars_support,arson_bars_near_coords = support(bars_coord,arson_coord,2)

if(make_rule(arson_bars_support)):
	rules.append("Bars -> Arson")


'''
######### CHURCH ###########
church_df = pd.read_csv('church_overlap.csv',names=['a','b','c','d','Lat', 'Long'],skiprows=1)
church_coord = church_df[['Lat','Long']].values.tolist()

'''
print()

print('**** CHURCH ****')
arson_church_support,arson_church_near_coords = support(church_coord,arson_coord,2)

if(make_rule(arson_church_support)):
	rules.append("Church -> Arson")



print()


print('**** bars and police ****')
arson_barpolice_support,arson_barpolice_near_coords = support1(clist,arson_coord,2)

if(make_rule(arson_barpolice_support)):
	rules.append("Bars, Police-> Arson")



print('**** RULES ****')
print(rules)


'''


trans = []
tot = 0
for a in drange(41.864974,41.952730,0.005):
	for b in drange(-87.807500, -87.595429,0.005):
		temp = []
		police = 0
		church = 0
		bars = 0
		arson = 0

		for i in arson_coord:
			if (i[0]>=a) and (i[1]>=b) and (i[0]<(a+0.005)) and (i[1]<(b+0.005)):
				temp.append('arson')
				break
				

		for i in police_coord:
			if (i[0]>=a) and (i[1]>=b) and (i[0]<(a+0.005)) and (i[1]<(b+0.005)):
				temp.append('police')
				break

		for i in church_coord:
			if (i[0]>=a) and (i[1]>=b) and (i[0]<(a+0.005)) and (i[1]<(b+0.005)):
				temp.append('church')
				break


		for i in bars_coord:
			if (i[0]>=a) and (i[1]>=b) and (i[0]<(a+0.005)) and (i[1]<(b+0.005)):
				bars+=1
		
		if(bars>14):
			temp.append('bars')		


		trans.append(temp)
		

trans1 = []
for i in trans:
	if 'arson' in i:
		print(i)
		trans1.append(i)

nearbar=0
nearchurch =0
barchurch =0
for i in trans1:
	if 'bars' in i:
		nearbar+=1

	if 'church' in i:
		nearchurch+=1
		if 'bars' in i:
			barchurch+=1



print('Total :  ',len(trans1))
print()
print('Bar Support :  ',nearbar/len(trans1))
print()
print('church Support :  ',nearchurch/len(trans1))
print()
print('bar church Support :  ',barchurch/len(trans1))
print()
	

