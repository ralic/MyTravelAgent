import pyfoursquare as foursquare

def init():
	global FS
	clientID = "BBCFS0BLYGRTNEGWZFZYXBJ05MEEJ0UVA21P1CUIBQK3HNYK"
	clientSecret = "NZE55Y3UBQ0GOY5SGXARJL5HXI1BTO3V4VWCVP2ZZYDIKM2S"
	callback = ''

	auth = foursquare.OAuthHandler(clientID, clientSecret, callback)

	accessToken = "LOOD23HDGFTTDXRCPA5JBVEUQITWFPPC25EZSCCDTU2NORQ1"
	auth.set_access_token(accessToken)

	#Now let's create an API
	FS = foursquare.API(auth)

def searchLL(lat, lgn):
	ll = '%s,%s'%(str(lat), str(lgn))
	result = FS.venues_search(ll=ll)
	# print FS.venues(id = test.id).photos.items()[1][1][0][u'prefix']
	try:
		CountItems = FS.venues(id = result[0].id).photos.items()[1][1][0]
		#print CountItems['count']
		item = CountItems['items'][0]
		url = item['prefix'] + "720x720" + item['suffix']
		print url
	except:
		url = ""
	return result[0], url


init()

if __name__ == "__main__":
	print searchLL(-8.063542, -34.872891)
	# test = result
	# # print FS.venues(id = test.id).photos.items()[1][1][0][u'prefix']
	# CountItems = FS.venues(id = test.id).photos.items()[1][1][0]
	# print CountItems['count']
	# item = CountItems['items'][0]
	# url = item['prefix'] + "720x720" + item['suffix']
	# print url
	#print dir(FS.venues(id = test.id).photos)

	#print test.id
	#print type(test)
	#print dir(test)



#print dir(result[0])

#print result[0].name