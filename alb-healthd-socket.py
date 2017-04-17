#!/usr/bin/python
# Queries the ALB and determines if healthd is healthy
#
# Prints following codes for zabbix reporting:
#0.xx Looks Good.
#2 An Error Occurred.
#3.xx ip in ip tunnel error.
#4.xx http healthcheck error.
#5.xx https healthcheck error.
#N.xx xx represents percent down. 2.33 means that 33 percent of ip-in-ip tunnel is down.
#healthecks fail if below 50%

import sys
import signal
import telnetlib
from optparse import OptionParser
import StringIO

timeout=30
DEFAULT_HOST="localhost"
DEFAULT_PORT="10899"

def deadlinehandler(signum, frame):
  print "2"
  sys.exit(2)

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
    tn.read_until("220")
    tn.write("dump all\n")
    tn.write("quit\n")

    report = tn.read_all()
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
    if ipinipUp <= 0:
      return 3.0
    if httpUp <= 0:
      return 4.0
    if httpsUp <= 0:
      return 5.0
    #calculate percentage up.
    ipinipRatio = ipinipUp / float(ipinipTotal)
    httpRatio = httpUp / float(httpTotal)
    httpsRatio = httpsUp / float(httpsTotal)
    if options.debug:
      print "ipinip Ratio: " + str(ipinipRatio)
      print "http Ratio: " + str(httpRatio)
      print "https Ratio: " + str(httpsRatio)

    if ipinipRatio < 0.5 :
      val = ipinipRatio + 3
      return val
    elif httpRatio < 0.5 :
      val = httpRatio + 4
      return val
    elif httpsRatio < 0.5 :
      val = httpsRatio + 5
      return val
    else:
      pass
  except:
    deadlinehandler(2,3)
  return ipinipRatio

if __name__ == '__main__':
    signal.signal(signal.SIGALRM, deadlinehandler)
    signal.alarm(timeout)
    exitCode = main()
    print exitCode
    sys.exit(int(exitCode))
    signal.alarm(0)
