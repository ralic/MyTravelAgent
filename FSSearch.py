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
	return result[0]


init()

if __name__ == "__main__":
	result = searchLL(-8.063542, -34.872891)
	test = result
	print test.url
	print type(test)
	print dir(test)



#print dir(result[0])

#print result[0].name