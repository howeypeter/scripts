#!/usr/bin/python
# Converts arista_confd log entry into json format and determines if healthd meets quorum.
#
# Prints following codes for zabbix reporting:
#0 Looks Good.
#1 An Error Occurred.
#2 No healthchecks in past 15 minutes.
#3 6 or fewer checks are passing, this means 2 or fewer servers are up.
#4 2/3 of checks are down
#5 1/2 of checks are down
#
import sys
import json
import time
import datetime
import signal
from optparse import OptionParser

timeout=30

def deadlinehandler(signum, frame):
  print "1"
  exit(2)

def parse_cli():
    ''' CLI parser using OptionParser'''

    parser = OptionParser()
    parser.add_option('-d', '--debug',
                      dest='debug',
                      default=False,
                      help='Enable debug output',
                      action='store_true')
    parser.add_option('-l', '--logfile',
                      dest='logfile',
                      default=None,
                      help='Log file location override',
                      type='string',
                      action='store')
    return parser.parse_args()

def main():
  (options, args) = parse_cli()
  try:
    for line in reversed(open(options.logfile).readlines()):
      if "lastHealthdContact" in line.rstrip() :
        logFile = line.rstrip()
        break

    garbage, logFile = logFile.split("status: ",1)
    logFile = logFile.replace("'", '"')
    j = json.loads(logFile)

    #check date is newer than 10 mins
    lastHealthdContact = j["lastHealthdContact"]
    healthdContactUnixTime = time.mktime(datetime.datetime.strptime(lastHealthdContact, "%a %b %d %H:%M:%S %Y %Z").timetuple())
    current_time = int(time.time())
    oldiness = current_time - healthdContactUnixTime
    if oldiness > 900 :
	  print "2"
          exit(0)
    #check number up exceeds 2
    if int(j["checksUp"]) <= 6 :
  	  print "3"
	  exit(0)
    #check ratio
    upRatio = j["checksUp"] / float(j["totalChecksMonitored"])
    #if ratio below 34%
    if upRatio < 0.34 :
      print "4"
      exit(0)
	  #if ratio below 51%
    if upRatio < 0.51 :
      print "5"
      exit(0)
    print "0"
  except:
    deadlinehandler(2,3)
  return 0


if __name__ == '__main__':
    signal.signal(signal.SIGALRM, deadlinehandler)
    signal.alarm(timeout)
    main()
    signal.alarm(0)
