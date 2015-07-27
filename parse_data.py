import re
from pandas import DataFrame

with open('DATA.txt') as f:
	lines = f.readlines()

	### JUST TEMPORARY UNTIL DATA FORMAT IS FIXED
	timestamp = []
	vbat = []
	distance = []

	for line in lines: 
		d, v = line[:-3].split(';')
		timestamp.append(':'.join(v.split(':')[2:]))
		vbat.append(v.split(':')[1])
		distance.append(50 - float(d.split(':')[1]))

d = {'distance': distance, 'vbat': vbat, 'timestamp': timestamp}
data = DataFrame(d)
data.to_csv('hum.txt', index = False)