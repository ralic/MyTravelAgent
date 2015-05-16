import signal, sys, ssl

sys.path.append('./lib')

from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer
from optparse import OptionParser
import InsSearch as insta

class Client(WebSocket):

   def handleMessage(self):
      city = self.data
      locationList, locationIndex = insta.searchCity(city)
      point = locationList[-1]['location'].point
      lat, lgn = point.latitude, point.longitude
      #print type(self.data)
      sendStr = ' '.join([str(lat), str(lgn)])
      print sendStr
      self.sendMessage(sendStr.decode("utf-8"))

   def handleConnected(self):
      print "A socket is connected."
      pass

   def handleClose(self):
      print "A socket is closed."
      pass        


def initServer():
   client = Client
   server = SimpleWebSocketServer('', 8000, client)
   return server
   
def close_sig_handler(signal, frame):
   print ("\n\n[*] " + "Closing server...\n\n")
   server.close()
   sys.exit()

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
