from dateutil.parser import parse
import re
import numpy as np
from collections import Counter # ERASE


def ConstructDataset(response):

	datapoints = []
	labels = []

	erase = []

	# Iterate on each airport reports
	for airportIATA, registries in response.items():

		# Skip the last updated element from the data
		if airportIATA == "last_updated":
			continue

		for registryDate, content in registries.items():
			
			try:
				temp = []
				#print registryDate, airportIATA, content['state'], content['city'] 
				#print content['status']['reason'], content['status']['type']
				#print content['weather']['weather'], content['weather']['wind'], content['weather']['visibility'] 
				#print content['delay']
				
				# Erase the noise in the date and parse it
				parsedDate = parse(registryDate.split()[0])
				temp.append( parsedDate.day )
				temp.append( parsedDate.month )
				temp.append( str(parsedDate.strftime('%H')) )#temp.append( str(parsedDate.strftime('%H:%M')) )

				temp.append( airportIATA )
				temp.append( content['state'] )
				temp.append( content['city'] )
				
				''' This features should not be used for prediction '''
				#temp.append(content['status']['reason']) SCARSE DATA, USE NAIVE
				#temp.append(content['status']['type']) # Scarse data but consistent
				temp.append( re.findall( "[-+]?\d+\.\d+", content['weather']['temp'] )[1] ) # 0 - F or 1 - C
				temp.append( weatherSelection(content['weather']['weather']) ) 
				
				(wind, direction) = WindDirectionExtraction(content['weather']['wind'])
				temp.append( wind )
				temp.append( direction )

				temp.append( content['weather']['visibility'] )
				
				# Add the registry to the dataset
				datapoints.append(temp)
				labels.append(content['delay'])
				
				
			# In case there is no available weather, the registry is skipped.
			except Exception, e:
				print "Error:", e, " not available"

	temp = []
	for word, count in Counter(erase).items():
		temp.append((count, word))
	for x in sorted(temp, reverse=True):
		print x

			
	# Permute the data before returning it as a dataset
	p = np.random.permutation(len(labels))

	datapoints = np.array(datapoints)
	labels = np.array(labels)

	return (datapoints[p], labels[p])


# SCARSE DATA, USE probabilistic model instead of rules
def weatherSelection(weather):

	if "and Breezy" in weather or "and Windy" in weather:
		return weather.split("and")[0].strip()
	else:
		return weather.strip()

def WindDirectionExtraction(windDirection):

	windDir = windDirection.split("at")

	direction = windDir[0].strip()
	wind = re.findall( "\d+\.\d+", windDir[1])[0]

	return (wind, direction)