import math
import pandas as pd

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

	total = len(coord1)*len(coord2)
	near=0
	qualified = []

	for a in coord1:
		for b in coord2:
			dist = haversine(a,b)
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



def make_rule(sup,threshold):
	if sup>threshold:
		return True
	else:
		return False


'''


police_station_file = open('police_station_clean.csv','r')

police_coord = []

for line in police_station_file:
    police_station_name, police_station_description, police_station_address, police_station_zip, police_station_lat, police_station_long = line.split(',')
    police_station_long = police_station_long.rstrip('\n')
    police_coord.append((police_station_lat, police_station_long))

#print(police_coord)
'''

rules = []


police_station_df = pd.read_csv('police_overlap.csv',names=['UID', 'Name', 'Desc', 'Zip', 'Lat', 'Long'],skiprows=1)
police_coord = police_station_df[['Lat','Long']].values.tolist()


#print(police_coord)



arson_df = pd.read_csv('arson.csv',names=['Date','Desc','Lat', 'Long','Loc','Block'],skiprows=1)
arson_coord = arson_df[['Lat','Long']].values.tolist()


#print(arson_coord)


arson_police_support,arson_police_near_coords = support(police_coord,arson_coord,2)

if(make_rule(arson_police_support,0.05)):
	rules.append("Police Station -> Arson")

print(rules)

