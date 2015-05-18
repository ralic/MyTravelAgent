# This module implements all the instagram data mining
# Token file "token.txt" needed in the same directory for this module

import sys
import os

from instagram.client import InstagramAPI

import Cities

global __ACCESS_TOKEN__
global ins


def init():
    global __ACCESS_TOKEN__
    global ins
    __ACCESS_TOKEN__ = getToken()
    ins = InstagramAPI(access_token=__ACCESS_TOKEN__, client_id="clientID", client_secret="clientSecret")


def getToken():
    try:
        with open("token.txt", "r") as f:
            for line in f:
                return line.strip()
    except IOError as e:
        print(os.strerror(e.errno))  
        sys.exit(0)

def searchCity(city, num):
    locationList = []
    locationIndex = {}
    tmp = Cities.findLocation(city)
    if tmp == -1:
        return -1
    lat, lng = tmp
    mediaList = ins.media_search(count=100, lat=lat, lng=lng, q=2000)#, min_timestamp=1431216000, max_timestamp=1431737117)
    print "Media Searched: " + str(len(mediaList))
    for media in mediaList:
        #print repr(dir(media))
        #print media.get_thumbnail_url()
        #print media.get_low_resolution_url()
        #print media.get_standard_resolution_url()
        #print media.images['thumbnail'].url
        locationID = media.location.id
        if locationID == "0":
            continue
        tags = []
        captions = []
        images = [media.images]
        try:
            tags += media.tags
        except:
            pass
        try:
            raw = media.caption.text
            rawList = raw.split()
            removeList = []
            for word in rawList:
                if "#" in word:
                    removeList.append(word)
                elif "@" in word:
                    removeList.append(word)
            for word in removeList:
                rawList.remove(word)
            text = ' '.join(rawList)
            captions.append(text)
        except:
            pass
        try: 
            index = locationIndex[locationID]
            locationDict = locationList[index]
            locationDict['tags'] += tags
            locationDict['captions'] += captions
            locationDict['images'] += images
        except:
            index = len(locationList)
            locationDict = {'locationID': locationID, \
                            'location': media.location, \
                            'tags': tags, \
                            'captions': captions, \
                            'images': images, \
                            'simScore': 0.0}
            locationList.append(locationDict)
            locationIndex[locationID] = index
        #print repr(dir(locationList[-1]['location'].point))
    try: 
        locationList = locationList[:num]
    except:
        "oops"
        pass
    return locationList, locationIndex
     #print repr(dir(media))

init()

if __name__ == "__main__":
    searchCity("New York")