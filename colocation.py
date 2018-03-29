import math


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




police_station_file = open('police_station_clean.csv','r')

police_coord = {}

police_dict[city] = [float(lati), float(longi)]

for line in police_station_file:
    police_station_name, police_station_description,police_station_address,police_station_zip,police_station_lat,police_station_long = line.split();
    print(police_station_zip)


