from dateutil.parser import parse
import re
import numpy as np
from collections import Counter # ERASE
import os.path # erase


def ConstructDataset(response):

	datapoints = []
	labels = []

	erase = []

	#if not os.path.exists("./airportIATA.txt"):
	dic = writeCities_Airports(response)

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
				temp.append( parsedDate.strftime('%H') )#temp.append( str(parsedDate.strftime('%H:%M')) )

				#temp.append( airportIATA )
				#temp.append( content['state'] )
				#temp.append( content['city'] )
				IATA, city, state = getAirportBinarizedRepresentation(dic, airportIATA)
				temp.extend(IATA)
				temp.extend(city)
				temp.extend(state)

				''' This features should not be used for prediction '''
				#temp.append(content['status']['reason']) SCARSE DATA, USE NAIVE
				#temp.append(content['status']['type']) # Scarse data but consistent
				temp.append( re.findall( "[-+]?\d+\.\d+", content['weather']['temp'] )[1] ) # 0 - F or 1 - C
				temp.append( weatherSelection(content['weather']['weather']) )
<<<<<<< HEAD
				
=======

>>>>>>> master
				(wind, direction) = WindDirectionExtraction(content['weather']['wind'])
				temp.append( wind )
				temp.extend( direction )

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

''' Read and Write to a File the cities and airports for HotEncoding '''
def writeCities_Airports(response):

	dic = {}

	states = {}
	cities = {}

	cIATA = cCity = cState = 0
	for airportIATA, registries in response.items():

		if airportIATA == "last_updated":
			continue

		if not dic.has_key(airportIATA):
			dic[airportIATA] = {"code": cIATA}

		cIATA = cIATA +1

		for registryDate, content in registries.items():
			if not states.has_key(content['state']):
				states[content['state']] = cState
				cState = cState + 1

			if not cities.has_key(content['city']):
				cities[content['city']] = cCity
				cCity = cCity + 1

			dic[airportIATA]["state"] = {"name": content['state'], "code": states[content["state"]]}
			dic[airportIATA]["city"] = {"name": content['city'], "code": cities[content["city"]]}

	dic["EXTRAS"] = { "maxIATA": cIATA, "maxCity": cCity, "maxState": cState }

	'''
	f_airports = open('airportIATA.txt', 'w')
	map(lambda x: f_airports.write(str(x[0])+" "+x[1]+"\n"), enumerate(IATA))
	f_airports.close()

	f_states = open('US_States.txt', 'w')
	map(lambda x: f_states.write(str(x[0])+" "+x[1]+"\n"), enumerate(states))
	f_states.close()

	f_cities = open('US_Cities.txt', 'w')
	map(lambda x: f_cities.write(str(x[0])+" "+x[1]+"\n"), enumerate(cities))
	f_cities.close()
	'''

	return dic

def getAirportBinarizedRepresentation(dic, IATA):

	IATACode = dic[IATA]["code"]
	cityCode = dic[IATA]["city"]["code"]
	stateCode = dic[IATA]["state"]["code"]

	IATA_vector = np.zeros(int(dic["EXTRAS"]["maxIATA"]))
	city_vector = np.zeros(int(dic["EXTRAS"]["maxCity"]))
	state_vector = np.zeros(int(dic["EXTRAS"]["maxState"]))

	IATA_vector[IATACode] = 1
	city_vector[cityCode] = 1
	state_vector[stateCode] = 1

	return np.concatenate([IATA_vector, city_vector, state_vector])


# SCARSE DATA, USE probabilistic model instead of rules
def weatherSelection(weather):

	if "and Breezy" in weather or "and Windy" in weather:
		return weather.split("and")[0].strip()
	else:
		return weather.strip()

def WindDirectionExtraction(windDirection):

	windDir = windDirection.split("at")

	directions = {
		"North": (0, 1),
		"Northwest": (-1,1),
		"West": (-1, 0),
		"Southwest": (-1, -1),
		"South": (0,-1),
		"Southeast": (1,-1),
		"East": (1, 0),
		"Northeast": (1, 1),
		"Variable": (0, 0)
	}

	direction = directions[ windDir[0].strip() ]
	wind = re.findall( "\d+\.\d+", windDir[1])[0]

	return (wind, direction)
