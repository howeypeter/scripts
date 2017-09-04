#!/usr/bin/python
import hashlib
import hmac
import time
import os
import ConfigParser
import urllib
import urllib2

try: import simplejson as json
except ImportError: import json
class hmacLLNW:
  def generateSecurityToken(self, url, httpMethod, apiKey, queryParameters=None,postData=None):
    global timestamp 
    timestamp = str(int(round(time.time()*1000)))
    datastring = httpMethod + url
    if queryParameters != None : datastring += queryParameters
    datastring += timestamp
    if postData != None : datastring += postData
    token = hmac.new(apiKey.decode('hex'), msg=datastring,digestmod=hashlib.sha256).hexdigest()
    return token
if __name__ == '__main__':
  profile='default'
  config = ConfigParser.RawConfigParser()
  config.read([os.path.expanduser('~/.llnw/credentials')])
  userName = config.get(profile, 'userName')
  apiKey = config.get(profile, 'apiKey')
  apiEndpoint = config.get(profile, 'apiEndpoint')
  queryParameters = ""
  postData = ""
  urL = apiEndpoint + "/svcinst/delivery/manual/shortname/shutterfly"
  #urL = apiEndpoint + "/svcinst/delivery/shortname/shutterfly" + queryParameters
  tool = hmacLLNW()
  hmac = tool.generateSecurityToken(url=urL, httpMethod="GET",queryParameters=queryParameters, postData=postData, apiKey=apiKey)
  token = json.dumps(hmac, indent=4)
  #toKen = token.split('"')[1]
  toKen = hmac
  req = urllib2.Request(urL)
  req.add_header('X-LLNW-Security-Principal', userName)
  req.add_header('X-LLNW-Security-Timestamp', timestamp)
  req.add_header('X-LLNW-Security-Token', toKen)
  print urL
  try:
    response = urllib2.urlopen(req).code
    print response
  except:
    print "fatal exception trying to get URL"
