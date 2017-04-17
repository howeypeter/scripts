#!/usr/bin/python
# howey.peter@gmail.com

import sys
import signal
import os
import subprocess
from optparse import OptionParser
import StringIO

import iscpy

timeout=297

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
    parser.add_option('-p', '--path',
                      dest='basepath',
                      default='/var/named/',
                      help='Path to config directory (/var/named/)',
                      action='store')
    parser.add_option('-c', '--config',
                      dest='conffile',
                      default='/etc/named.conf',
                      help='The path to the BIND config file (/etc/named.conf)',
                      type='string',
                      action='store')

    return parser.parse_args()

def get_zones(filename):
	try:
		domainList=[]
		with open(filename) as bind_config_file:
			bind_string = bind_config_file.read()
			bind_dict = iscpy.ParseISCString(bind_string)
			for zone in bind_dict.iteritems():
				if "zone " in str(zone) and "file" in str(zone):
					zoneDomain=zone[0]
					zoneDomain=zoneDomain.replace("zone ","")
					zoneDomain= zoneDomain.replace("\"","")
					zoneDomain= zoneDomain.replace("\'","")
					dict=zone[1]
					zoneType=dict['type']
					zoneType=zoneType.replace("\"","")
					zoneType=zoneType.replace("\'","")
					zoneFile=dict['file']
					zoneFile=zoneFile.replace("\"","")
					zoneFile=zoneFile.replace("\'","")
					tup=(zoneDomain,zoneType,zoneFile)
					domainList.append(tup)
	except:
		print "get_zones failure"
		deadlinehandler(2,3)
	return domainList

def check_conf(config):
	try:
		cmd="/usr/sbin/named-checkconf " + config
		cmdResult=os.system(cmd)
		if (cmdResult !=0):
			print "check_conf failure"
			deadlinehandler(2,3)
		return cmdResult
	except:
		print "check_conf failure"
		deadlinehandler(2,3)

def check_files(base,listZones):
	try:
		for tup in listZones:
			if (tup[1]=='master'):
				if (os.path.isfile(base + tup[2]) == False):
					print "check_files failed; a file is missing"
					deadlinehandler(2,3)
		return 0
	except:
		print "check_files failure"
		deadlinehandler(2,3)

def check_zone(base,domainList,debug):
	try:
		for tup in domainList:
			if (tup[1] != 'hint'):
				cmd="/usr/sbin/named-checkzone " + tup[0] + " " + base + tup[2]
				#print cmd
				#cmd=str("/usr/sbin/named-checkzone " + tup[0] + " " + base + tup[2] )
				#cmdResult=subprocess.call([cmd], stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
                		#cmdResult=os.system(cmd,/dev/null)

				fullpath=str(base + tup[2])
				if debug is True:
					print "Checking Zone: " + str(tup[0])
				command = ["/usr/sbin/named-checkzone", tup[0], fullpath]

				with open(os.devnull, "w") as fnull:
					cmdResult = subprocess.call(command, stdout = fnull, stderr = fnull)
                		if (cmdResult != 0 ):
					print "check_zone failure"
					deadlinehandler(2,3)
	except:
		print "check_zone failure"
		deadlinehandler(2,3)
	return 0

def main():
	(options, args) = parse_cli()
	try:
		zoneList=get_zones(options.conffile)
		#print zoneList
		e=check_conf(options.conffile)
		f=check_files(options.basepath,zoneList)
		g=check_zone(options.basepath,zoneList,options.debug)

	except:
		deadlinehandler(2,3)
	return 0

if __name__ == '__main__':
	signal.signal(signal.SIGALRM, deadlinehandler)
	signal.alarm(timeout)
	main()
	print "0"
	signal.alarm(0)
