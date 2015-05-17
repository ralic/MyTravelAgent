import signal, sys, ssl, string, traceback

sys.path.append('./lib')

from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer
from optparse import OptionParser
import InsSearch as insta
import WordAnalysis as wa
import FSSearch as fs
import Cities, Sentiment

STAR = "^ ^ ^"
TRI = "$ $ $"

SEND_STR = "H2^ ^ ^42.3589,-71.05786$ $ $Old State House$ $ $https://scontent.cdninstagram.com/hphotos-xaf1/t51.2885-15/e15/11272407_715808588547924_993920908_n.jpg^ ^ ^42.358081012,-71.054919232$ $ $Beantown Hoagie$ $ $https://scontent.cdninstagram.com/hphotos-xaf1/t51.2885-15/e15/11272861_705525536237047_1595948651_n.jpg^ ^ ^42.355373,-71.059817$ $ $Roche Bros Downtown Crossing$ $ $https://scontent.cdninstagram.com/hphotos-xaf1/t51.2885-15/e15/11244040_1428580840782007_519173520_n.jpg"

TAGPOOL = ['nofilter', 'fun', 'blessed', 'sweet', 'yay', 'love', 'pray']
TAG_COUNT = 0

class Client(WebSocket):

   def handleMessage(self):
      recv = self.data.split(STAR)
      header = recv[0].strip()
      if header == "H1":
         print "city requested"
         city = recv[1].strip()
         self.cityRequest(city)
      elif header == "H2":
         print "text requested"
         text = recv[1].strip()
         # self.sendStr(SEND_STR)
         # print "sent"
         try:
            #pass
            self.textRequest(text)
         except:
            print "Unexpected error:", sys.exc_info()[0]
            print (traceback.format_exc())
            raise
      else:
         print "invalid request"
      # city = self.data
      # locationList, locationIndex = insta.searchCity(city)
      # point = locationList[-1]['location'].point
      # thumbnail = locationList[-1]['images'][0]['standard_resolution'].url
      # #caption = ' '.join([locationList[-1]['captions'][0], locationList[-1]['tags'][0]])
      # #print "Caption: " + caption
      # lat, lng = point.latitude, point.longitude
      # #print type(self.data)
      # toSend = '\t'.join([str(lat), str(lng), thumbnail])
      # print 'Sending String: ' + sendStr
      # self.sendStr(toSend)

   def handleConnected(self):
      print "A socket is connected."
      pass

   def handleClose(self):
      print "A socket is closed."
      pass        


   def sendStr(self, string):
      self.sendMessage(string.decode("utf-8"))

   def cityRequest(self, city):
      city = city.lower()

      tmp = Cities.findLocation(city)
      if tmp == -1:
         toSend = STAR.join(['H1', '-1'])
         self.sendStr(toSend)
         print "city not found"
         return -1
      self.city = city
      lat, lng = tmp
      ll = str(lat) + ',' + str(lng)
      locationList, locationIndex = insta.searchCity(city)
      print "grams searched: " + str(len(locationList))
      locationList = locList24(locationList)
      print "sent pics num:" + str(len(locationList))
      toSend = STAR.join(['H1', '0', ll, locList2str(locationList)])
      print toSend
      self.sendStr(toSend)
      print "sent"
      return

   def textRequest(self, text):
      locationList, locationIndex = insta.searchCity(self.city)
      print "grams searched: " + str(len(locationList))
      # filter the locations with negative sentiment
      removeList = []
      for locationDict in locationList:
         captions = locationDict['captions']
         if not Sentiment.judgeSetSentiment(captions):
            removeList.append(locationDict)
      print "finished sentiment judging"
      for locationDict in removeList:
         locationList.remove(locationDict)
      # get the locations with top three similarities
      text = "".join(l for l in text if l not in string.punctuation)
      print text
      textList = text.split()
      for locationDict in locationList:
         tags = locationDict['tags']
         for i in range(0, len(tags)):
            tags[i] = tags[i].name.strip("#")
         simScore = wa.getSetsSim(tags, textList)
         locationDict['simScore'] = simScore
      print "finished similarities"
      topThree = getTopLocation(locationList, 3)
      stringList = []
      for locationDict in topThree:
         point = locationDict['location'].point
         lat, lng = point.latitude, point.longitude
         ll = str(lat) + ',' + str(lng)
         searchLLResult, searchUrl = fs.searchLL(lat, lng)
         txt = searchLLResult.name
         #imageUrl = locationDict['images'][0]['standard_resolution'].url
         if searchUrl == "":
            imageUrl = locationDict['images'][0]['standard_resolution'].url
         else:
            imageUrl = searchUrl
         stringList.append(TRI.join([ll, txt, imageUrl]))      
      toSend = STAR.join(['H2'] + stringList)
      print toSend
      self.sendStr(toSend)
      print "sent"





def initServer():
   client = Client
   server = SimpleWebSocketServer('', 8000, client)
   return server
   
def close_sig_handler(signal, frame):
   print ("\n\n[*] " + "Closing server...\n\n")
   server.close()
   sys.exit()

def locList2str(locationList):
   stringList = []
   for locationDict in locationList:
      point = locationDict['location'].point
      lat, lng = point.latitude, point.longitude
      ll = str(lat) + ',' + str(lng)
      tags = locationDict['tags']
      tag = "x" * 9
      if len(tags) == 0:
         print "picking pool cos no tag"
         tag = pickTagPool()
      else:
         for t in tags:
            t = t.name
            try:
               t.decode("utf-8")
            except:
               continue
            if len(t.strip("#")) < 8:
               tag = t
               break
         if (len(tag) > 7):
            print "picking pool cos too long"
            t = pickTagPool()
            tag = t
      tag = tag.strip("#").upper()
      tag = "#" + tag
      imageUrl = locationDict['images'][0]['standard_resolution'].url
      stringList.append(TRI.join([ll, tag, imageUrl]))
   return STAR.join(stringList)





   # TODO send top three info

def pickTagPool():
   global TAG_COUNT 
   global TAGPOOL
   TAG_COUNT += 1
   result = TAGPOOL[TAG_COUNT % len(TAGPOOL)]
   return result

def locList24(locationList):
   while (len(locationList) < 24):
      locationList += locationList
   return locationList[:24]


def getMaxLocation(locationList):
   maxScore = 0.0
   maxLocation = None
   for locationDict in locationList:
      if locationDict['simScore'] > maxScore:
         maxLocation = locationDict
         maxScore = locationDict['simScore']
   return maxLocation



def getTopLocation(locationList, topNum):
   while len(locationList) < 3:
      locationList += locationList
   top = []
   for i in range(0, topNum):
      maxLocation = getMaxLocation(locationList)
      top.append(maxLocation)
      locationList.remove(maxLocation)
   return top


if __name__ == "__main__":

   # parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
   # parser.add_option("--host", default='', type='string', action="store", dest="host", help="hostname (localhost)")
   # parser.add_option("--port", default=8000, type='int', action="store", dest="port", help="port (8000)")
   # parser.add_option("--ssl", default=0, type='int', action="store", dest="ssl", help="ssl (1: on, 0: off (default))")
   # parser.add_option("--cert", default='./cert.pem', type='string', action="store", dest="cert", help="cert (./cert.pem)")
   # parser.add_option("--ver", default=ssl.PROTOCOL_TLSv1, type=int, action="store", dest="ver", help="ssl version")
   
   # (options, args) = parser.parse_args()

   # cls = SimpleEcho

   # if options.ssl == 1:
   #    server = SimpleSSLWebSocketServer(options.host, options.port, cls, options.cert, options.cert, version=options.ver)
   # else:	
   #    server = SimpleWebSocketServer(options.host, options.port, cls)

   server = initServer()


   signal.signal(signal.SIGINT, close_sig_handler)

   server.serveforever()
