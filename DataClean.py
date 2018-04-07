import pandas as pd

crime_df = pd.read_csv('crime_overlap2.csv',names=['Date','Desc','Lat', 'Long','Loc','Block'],skiprows=1)
crime_list = crime_df[['Desc','Lat','Long']].values.tolist()

police_station_df = pd.read_csv('police_overlap.csv',names=['UID', 'Name', 'Desc', 'Zip', 'Lat', 'Long'],skiprows=1)
police_coord = police_station_df[['Lat','Long']].values.tolist()

bars_df = pd.read_csv('bars_overlap.csv',names=['a','b','c','d', 'e', 'f', 'g', 'Lat', 'Long'],skiprows=1)
bars_coord = bars_df[['Lat','Long']].values.tolist()

library_df = pd.read_csv('library_overlap.csv',names=['a','b','c','d','Lat', 'Long'],skiprows=1)
library_coord = library_df[['Lat','Long']].values.tolist()

church_df = pd.read_csv('church_overlap.csv',names=['a','b','c','d','Lat', 'Long'],skiprows=1)
church_coord = church_df[['Lat','Long']].values.tolist()

school_df = pd.read_csv('school_overlap.csv',names=['a','b','c','d','Lat', 'Long'],skiprows=1)
school_coord = school_df[['Lat','Long']].values.tolist()

feature_coord = [police_coord,library_coord,school_coord,church_coord,bars_coord]

features = []
ind = 0
for i in feature_coord:
	ind+=1
	tmp = str(ind)
	tmp += '.csv'
	with open(tmp, "w") as outfile:
		for entries in i:
			for e in entries:
				outfile.write(str(e))
				outfile.write(", ")
			outfile.write("\n")
	features.append(tmp)

with open('features.txt', "w") as outfile:
	for entries in features:
		for e in entries:
			outfile.write(e)
		outfile.write(", ")
		
			