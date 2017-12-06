# This module implements the lookup for Major US cities
# "cities.txt" needed in the same directory for this module

global __MAJOR_CITIES__
global __CITY_INDEX__

__MAJOR_CITIES__ = []
__CITY_INDEX__ = {}

def init():
	global __MAJOR_CITIES__
	with open("cities.txt", "r") as f:
		for line in f:
			line = line.strip()
			if line == "":
				continue
			if line[0] != "#":
				elements = line.split("\t")
				latitude = float(elements[1].strip())
				longitude = float(elements[2].strip())
				tmp = elements[-1].split("#")
				city = tmp[0].strip()
				state = tmp[1].strip()
				cityDict = {'city': city.lower(), 'latitude': latitude, 'longitude': longitude, 'state': state}
				__MAJOR_CITIES__.append(cityDict)
	for i in range(0, len(__MAJOR_CITIES__)):
		city = __MAJOR_CITIES__[i]['city']
		index = i
		__CITY_INDEX__[city] = index


def findLocation(city):
	city = city.lower()
	try:
		index = __CITY_INDEX__[city]
	except:
		return -1
	cityDict = __MAJOR_CITIES__[index]
	latitude = cityDict['latitude']
	longitude = cityDict['longitude']
	state = cityDict['state']
	return latitude, longitude

init()

if __name__ == "__main__":
	print(findLocation("Boston"))



