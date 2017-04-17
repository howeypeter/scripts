#!/usr/bin/python
# Queries the ALB and determines if healthd is healthy
#
# Prints following codes for zabbix reporting:
#0 Looks good
#1 A problem with the script.
#2 ip in ip tunnel problem.
#3 http healthcheck problem.
#4 https healthcheck problem.
#healthcheck fails if below 3 healthchecks are passing.
#script fails if below 20% up for any of the 3 service-checks.

import sys
import signal
import telnetlib
from optparse import OptionParser
import StringIO

timeout=30
DEFAULT_HOST="localhost"
DEFAULT_PORT="10899"

def deadlinehandler(signum, frame):
  print "1"
  sys.exit(1)

def parse_cli():
    ''' CLI parser using OptionParser'''

    parser = OptionParser()
    parser.add_option('-d', '--debug',
                      dest='debug',
                      default=False,
                      help='Enable debug output',
                      action='store_true')
    parser.add_option('-H', '--host',
                      dest='host_name',
                      default=DEFAULT_HOST,
                      help='Default hostname override',
                      type='string',
                      action='store')
    parser.add_option('-P', '--port',
                      dest='port',
                      default=DEFAULT_PORT,
                      help='Default port override',
                      type='string',
                      action='store')

    return parser.parse_args()

def main():
  (options, args) = parse_cli()
  #connect to healthd and dump the status.
  try:
    tn = telnetlib.Telnet(options.host_name,options.port,timeout)
    tn.read_until("220",20)
    tn.write("dump all\n")
    report = tn.read_until("dump complete",20)
    tn.write("quit\n")
    tn.close()

  except:
    deadlinehandler(2,3)
  #check the number of healthchecks up versus the number of healthchecks total.
  try:
    ipinipTotal = 0
    ipinipUp = 0
    httpsTotal = 0
    httpsUp = 0
    httpTotal = 0
    httpUp = 0

    for line in StringIO.StringIO(report):
      if "ipinip" in line.rstrip():
        ipinipTotal += 1
        if "UP" in line.rstrip():
          ipinipUp += 1
      elif "https" in line.rstrip():
        httpsTotal += 1
        if "UP" in line.rstrip():
          httpsUp += 1    
      elif "http" in line.rstrip():
        httpTotal += 1
        if "UP" in line.rstrip():
          httpUp += 1
      else:
        pass
    if options.debug:
      print "IP Tunnel Up: " + str(ipinipUp)
      print "IP Tunnel Total: " + str(ipinipTotal)
      print "HTTP Up: " + str(httpUp)
      print "HTTP Total: " + str(httpTotal)
      print "HTTPS Up: " + str(httpsUp)
      print "HTTPS Total: " + str(httpsTotal)

  except:
    deadlinehandler(2,3)

  try:
    #at least 2 servers must be up.
    if ipinipUp <= 2:
      return 2
    if httpUp <= 2:
      return 3
    if httpsUp <= 2:
      return 4
    #calculate percentage up.
    ipinipRatio = ipinipUp / float(ipinipTotal)
    httpRatio = httpUp / float(httpTotal)
    httpsRatio = httpsUp / float(httpsTotal)
    if options.debug:
      print "ipinip Ratio: " + str(ipinipRatio)
      print "http Ratio: " + str(httpRatio)
      print "https Ratio: " + str(httpsRatio)
    #at least 20% should be available.
    if ipinipRatio < 0.2 :
      return 2
    elif httpRatio < 0.2 :
      return 3
    elif httpsRatio < 0.2 :
      return 4
    else:
      pass
  except:
    deadlinehandler(2,3)
  return 0

if __name__ == '__main__':
    signal.signal(signal.SIGALRM, deadlinehandler)
    signal.alarm(timeout)
    exitCode = main()
    print exitCode
    sys.exit(int(exitCode))
    signal.alarm(0)
