import math
import pandas as pd
import numpy as nmp
#import matplotlib.pyplot as plt
import time
start = time.time()



rules = []

clist = []


def drange(start, stop, step):
    while start < stop:
            yield start
            start += step


#data extraction

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


arson_coord = ['ARSON']
assault_coord = ['ASSAULT']
burglary_coord = ['BURGLARY']
homicide_coord = ['HOMICIDE']
damage_coord = ['CRIMINAL DAMAGE']
trespass_coord = ['CRIMINAL TRESPASS']
humantraff_coord = ['HUMAN TRAFFICKING']
interference_coord = ['INTERFERENCE WITH OFFICER']
liquor_coord = ['LIQUOR']
kidnap_coord = ['KIDNAP']
vehicle_coord = ['VEHICLE THEFT']
narcos_coord = ['NARCOTICS']
child_coord = ['OFFENSE INVOLVING CHILDREN']
prost_coord = ['PROSTITUTION']
robbery_coord = ['ROBBERY']
sex_coord = ['SEX OFFENSE']
theft_coord = ['THEFT']
weapons_coord = ['WEAPONS VIOLATION']

seg_crimes = []

ctr_means = []
ctr1 = [-1] * 18

for i in crime_list:
	if i[0] == 'ARSON':
		arson_coord.append((i[1],i[2]))
		ctr1[0]+=1

	if i[0] == 'ASSAULT':
		assault_coord.append((i[1],i[2]))
		ctr1[1]+=1

	if i[0] == 'BURGLARY':
		burglary_coord.append((i[1],i[2]))
		ctr1[2]+=1

	if i[0] == 'HOMICIDE':
		homicide_coord.append((i[1],i[2]))
		ctr1[3]+=1

	if i[0] == 'CRIMINAL DAMAGE':
		damage_coord.append((i[1],i[2]))
		ctr1[4]+=1

	if i[0] == 'CRIMINAL TRESPASS':
		trespass_coord.append((i[1],i[2]))
		ctr1[5]+=1

	if i[0] == 'HUMAN TRAFFICKING':
		humantraff_coord.append((i[1],i[2]))
		ctr1[6]+=1

	if i[0] == 'INTERFERENCE WITH PUBLIC OFFICER':
		interference_coord.append((i[1],i[2]))
		ctr1[7]+=1

	if i[0] == 'LIQUOR LAW VIOLATION':
		liquor_coord.append((i[1],i[2]))
		ctr1[8]+=1

	if i[0] == 'KIDNAPPING':
		kidnap_coord.append((i[1],i[2]))
		ctr1[9]+=1	

	if i[0] == 'MOTOR VEHICLE THEFT':
		vehicle_coord.append((i[1],i[2]))
		ctr1[10]+=1

	if i[0] == 'NARCOTICS':
		narcos_coord.append((i[1],i[2]))
		ctr1[11]+=1

	if i[0] == 'OFFENSE INVOLVING CHILDREN':
		child_coord.append((i[1],i[2]))
		ctr1[12]+=1

	if i[0] == 'PROSTITUTION':
		prost_coord.append((i[1],i[2]))
		ctr1[13]+=1

	if i[0] == 'ROBBERY':
		robbery_coord.append((i[1],i[2]))
		ctr1[14]+=1

	if i[0] == 'SEX OFFENSE':
		sex_coord.append((i[1],i[2]))
		ctr1[15]+=1

	if i[0] == 'THEFT':
		theft_coord.append((i[1],i[2]))
		ctr1[16]+=1

	if i[0] == 'WEAPONS VIOLATION':
		weapons_coord.append((i[1],i[2]))
		ctr1[17]+=1	


for ct in ctr1:
	ctr_means.append(ct/774)

crimes_coord = [arson_coord,
assault_coord,
burglary_coord,
homicide_coord,
damage_coord,
trespass_coord,
humantraff_coord,
interference_coord,
liquor_coord,
kidnap_coord,
vehicle_coord,
narcos_coord,
child_coord,
prost_coord,
robbery_coord,
sex_coord,
theft_coord,
weapons_coord]


trans = []
tot = 0

for a in drange(41.864974,41.952730,0.005):
	for b in drange(-87.807500, -87.595429,0.005):
		
		temp = []
		police = 0
		church = 0
		bars = 0

		
		ctr = [0] * 18
		
		for c in crimes_coord:
			for i in range(1,len(c)):
				if (c[i][0]>=a) and (c[i][1]>=b) and (c[i][0]<(a+0.005)) and (c[i][1]<(b+0.005)):
					if c[0]=='ARSON':
						ctr[0]+=1
					if c[0]=='ASSAULT':
						ctr[1]+=1
					if c[0]=='BURGLARY':
						ctr[2]+=1
					if c[0]=='HOMICIDE':
						ctr[3]+=1
					if c[0]=='CRIMINAL DAMAGE':
						ctr[4]+=1
					if c[0]=='CRIMINAL TRESPASS':
						ctr[5]+=1
					if c[0]=='HUMAN TRAFFICKING':
						ctr[6]+=1
					if c[0]=='INTERFERENCE WITH OFFICER':
						ctr[7]+=1
					if c[0]=='LIQUOR':
						ctr[8]+=1
					if c[0]=='KIDNAP':
						ctr[9]+=1
					if c[0]=='VEHICLE THEFT':
						ctr[10]+=1
					if c[0]=='NARCOTICS':
						ctr[11]+=1
					if c[0]=='OFFENSE INVOLVING CHILDREN':
						ctr[12]+=1
					if c[0]=='PROSTITUTION':
						ctr[13]+=1
					if c[0]=='ROBBERY':
						ctr[14]+=1
					if c[0]=='SEX OFFENSE':
						ctr[15]+=1
					if c[0]=='THEFT':
						ctr[16]+=1
					if c[0]=='WEAPONS VIOLATION':
						ctr[17]+=1
		
		for ct in range(0,len(ctr)):
			if ctr[ct] >= ctr_means[ct]:
				temp.append(crimes_coord[ct][0])

				#print(crimes_coord[ct][0])


		for i in police_coord:
			if (i[0]>=a) and (i[1]>=b) and (i[0]<(a+0.005)) and (i[1]<(b+0.005)):
				temp.append('SCHOOL')
				break


		for i in library_coord:
			if (i[0]>=a) and (i[1]>=b) and (i[0]<(a+0.005)) and (i[1]<(b+0.005)):
				temp.append('LIBRARY')
				break


		for i in church_coord:
			if (i[0]>=a) and (i[1]>=b) and (i[0]<(a+0.005)) and (i[1]<(b+0.005)):
				temp.append('CHURCH')
				break


		for i in school_coord:
			if (i[0]>=a) and (i[1]>=b) and (i[0]<(a+0.005)) and (i[1]<(b+0.005)):
				temp.append('SCHOOL')
				break


		for i in bars_coord:
			if (i[0]>=a) and (i[1]>=b) and (i[0]<(a+0.005)) and (i[1]<(b+0.005)):
				bars+=1
		
		if(bars>14):
			temp.append('BARS')		


		trans.append(temp)




print(ctr1)
print(ctr_means)

#for g in ctr_list:
#	print(nmp.mean(g))	
for t in trans:
	print(t)
'''
plt.plot(sorted(assault_wt))
plt.show()
'''
'''
trans_arson = []
for i in trans:
	if 'arson' in i:
		print(i)
		trans_arson.append(i)

nearbar=0
nearchurch =0
barchurch =0
nearlib =0

for i in trans:
	if 'bars' in i:
		nearbar+=1

	if 'church' in i:
		nearchurch+=1

	if 'library' in i:
		nearlib+=1


print('Total :  ',len(trans_arson))
print()
print('Bar Support :  ',nearbar/len(trans1))
print()
print('church Support :  ',nearchurch/len(trans1))
print()
print('library Support :  ',nearlib/len(trans1))
print()
'''	



end = time.time()
print(end - start)



