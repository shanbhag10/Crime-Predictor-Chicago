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

'''


police_station_file = open('police_station_clean.csv','r')

police_coord = []

for line in police_station_file:
    police_station_name, police_station_description, police_station_address, police_station_zip, police_station_lat, police_station_long = line.split(',')
    police_station_long = police_station_long.rstrip('\n')
    police_coord.append((police_station_lat, police_station_long))

#print(police_coord)
'''

police_station_df = pd.read_csv('police_station_clean.csv',names=['UID', 'Name', 'Desc', 'Zip', 'Lat', 'Long'],skiprows=1)
police_coord = police_station_df[['Lat','Long']].values.tolist()


#print(police_coord)



arson_df = pd.read_csv('arson.csv',names=['Date','Desc','Lat', 'Long','Loc','Block'],skiprows=1)
arson_coord = arson_df[['Lat','Long']].values.tolist()


#print(arson_coord)

total_police_arson=0
near_police_arson=0
for arson in arson_coord:
	for police_station in police_coord:
		total_police_arson+=1
		dist = haversine(arson,police_station)
		if(dist<2):
			near_police_arson+=1
			print(dist)

print(near_police_arson)
print(total_police_arson)

print('Support : ', near_police_arson/total_police_arson)

