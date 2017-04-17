#!/usr/bin/python

import sys
import os
import ddutils
import socket
from optparse import OptionParser
import json
import urllib2
import pprint
socket.setdefaulttimeout(28)


class DDALERT(object):

    """  Class definition for DDoS Alerts
    """

    def __init__(self, options=None):
        """  Set up global names and defaults
             construct the headers we need for a REST API call
             read in the config and store in an instance variable
             authenticate to the API using username/pw information in
             the $HOME/.dai_alert_config file to obtain the session ID 
             and save that SID in an instance variable 
        """
        if options.debug:
            local_method = sys._getframe().f_code.co_name
            print 'DBG:DDALERT:BEGIN:', local_method
        self.options = options
        self.debug = options.debug
        self.attack_rows =[]
        self.attack_numrows = 0
        self.headers = {}
        self.headers.update({'Pragma': 'no-cache'})
        self.headers.update({'Connection': 'keep-alive'})
        self.headers.update({'Content-Type': 'application/json'})
        self.headers.update({'Accept': '*/*'})
        self.home_dir = os.path.expanduser("~")
        self.attack_status = {'Terminated' : 0 , 
                              'Started' : 1 , 
                              'Ongoing' : 2 ,
                              'Sampled' : 3 ,
                              'Occurred' : 4 }
        if options.debug:
            print 'DBG:DDALERT:%s:self.home_dir:%s' % (local_method,
                                                       self.home_dir)
        try:
            if options.config is None:
                config_file = self.home_dir + "/.dai_alert_config"
            else:
                config_file = options.config

            if options.debug:
                print 'DBG:DDALERT:%s:config_file:%s' % (local_method,
                                                         config_file)
            my_data = open(config_file).read()
            self.config_data = json.loads(my_data)
            self.hostname = self.config_data['hostname']
        except:
            raise RuntimeError('ERROR: Unable to read config file')
        if options.debug:
            print 'DBG:DDALERT:%s:self.config_data:%s' % (local_method,
                                                          self.config_data)
        try:
            url = 'https://%s/%s' % (self.config_data['hostname'],
                                     self.config_data['auth_path'])
            uname_passwd = json.dumps(
                {'username': self.config_data['username'], 
                 'password': self.config_data['password']})
            if options.debug:
                print 'DBG:DDALERT:%s:url:%s' % (local_method, url)
                print 'DBG:DDALERT:%s:uname_passwd:%s' % (local_method,
                                                      uname_passwd)
            api_auth_req = urllib2.Request(url, uname_passwd,
                                           headers=self.headers)
            api_response = urllib2.urlopen(api_auth_req)
            auth_response = json.loads(api_response.read())
            if options.debug:
                print 'DBG:DDALERT:%s:auth_response:%s' % (local_method, 
                                                           auth_response)
            if not auth_response['status'] == 'ok':
                print 'Bad HTTP return code:%s' % auth_response['status']
            self.sid = auth_response['jsessionid']
            self.headers.update({'JSESSIONID': self.sid})
        except:
            raise RuntimeError('ERROR: Unable to authenticate.')
        if options.debug:
            print 'DBG:DDALERT:%s:self.sid:%s' % (local_method, self.sid)
            print 'DBG:DDALERT:END:', local_method
        return

###############################################################################

    def get_attack_list(self):
        ''' method to retrieve attack table from Radware Vision
        retrieves attack table from past 24 hours, strips off the 
        request portion and assigns the number of rows and the attack table
        itself to instance variables
        '''
        if self.debug:
            local_method = sys._getframe().f_code.co_name
            print 'DBG:DDALERT:BEGIN:', local_method
        report_params = {"start": 0,
                         "count": 50,
                         "filter": {},
                         "reportScope": {"range": 1800,
                                         "devices": ["c59c07444b994bf3014c04a074e108ab","c59c07444b994bf3014be132552704d0","c59c07444b782af2014b7a03a3c93bc8","c59c07444b782af2014b7a2cab977570","c59c07444b994bf3014c29380d7e66d9"],
                                         "ports": {"source": [],
                                                   "dest": [],
                                                   "biDir": []},
                                         "policies": []},
                         "sort": [{"field": "startTime",
                                   "dir": "desc"}]}
        request_data = json.dumps(report_params)
        url = 'https://%s/%s' % (self.hostname, 
                                 self.config_data['report_path'])
        report_request = urllib2.Request(url, request_data,
                                         headers=self.headers)
        try:
            response = urllib2.urlopen(report_request)
            attacks = json.loads(response.read())
        except urllib2.URLError as error:
            print error
        self.attack_numrows = attacks['totalRows']
        self.attack_rows = attacks['rows']
        if self.debug:
            print 'DBG:DDALERT:%s:attacks:%s' % (local_method, attacks)
        if self.debug:
            print 'DBG:DDALERT:%s:Return True to caller' % (local_method)
            print 'DBG:DDALERT:%s:END' % (local_method)
        return True

###############################################################################

    def get_customer_shortname(self,ipaddr):
        ''' Pass in the IP address being attacked, use this to look up the
            shortname of the customer under attack and return the valid 
            shortname or None if the attack target doesn't match any shortname.

            eventually this should be done by a reverse DNS resolution on the 
            IP of the attack destination
        '''
        if self.debug:
            local_method = sys._getframe().f_code.co_name
            print 'DBG:DDALERT:BEGIN:', local_method
            print 'DBG:DDALERT:%s:ipaddr:%s' % (local_method, ipaddr)
        try:
            self.dbh = ddutils.DB(
                self.config_data['db_hostname'],
                self.config_data['db_username'],
                self.config_data['db_password'],
                self.config_data['db_name'])
            self.cursor = self.dbh.getCursor()
        except:
            raise RuntimeError('ERROR: Unable to connect to database')
        try:
            query = """SELECT * FROM ac_vips WHERE 
                       ac_vip_aside = '%s' """ % (ipaddr)
            if self.debug:
                print 'DBG:DDALERT:%s:query:%s' % (local_method, query)
            self.dbh.execute(query)
            row = self.dbh.fetchone()
        except:
            raise RuntimeError('ERROR: Problem retrieving data from database')
        if row is None:
            if self.debug:
                print 'DBG:DDALERT:%s:Return None to caller' % (local_method) 
                print 'DBG:DDALERT:%s:END' % (local_method) 
            return None 
        else:
            if self.debug:
                print 'DBG:DDALERT:%s:shortname:%s:' % (local_method,
                                                      row['shortname']) 
                print 'DBG:DDALERT:%s:END' % (local_method) 
            return row['shortname'] 


###############################################################################

    def get_new_alerts(self):
        ''' Get a list of alerts from Vision.  Repackage specific fields so
            Zabbix can consume the alert.
        '''

        if self.debug:
            local_method = sys._getframe().f_code.co_name
            print 'DBG:DDALERT:BEGIN:', local_method

        new_alert_list = []
        status = self.get_attack_list()

        for one_attack_row in self.attack_rows:
            attack_id = one_attack_row['attackIpsId'] 
            shortname = self.get_customer_shortname(one_attack_row['destAddress'])

            attack_string = one_attack_row['attackStatus']
            
            if attack_string == 'Started':
                break

            attack_status = self.attack_status[attack_string]

            name_list = socket.gethostbyaddr(one_attack_row['deviceIp'])
            device_name = name_list[0]
            single_alert = {  "{#SHORTNAME}" : shortname, 
                              "{#DPRO}" : device_name,
                              "{#ATTACKTYPE}" : one_attack_row['attackCategory'],
                              "{#ATTACKNAME}" : one_attack_row['attackName'],
                              "{#DESTIP}" : one_attack_row['destAddress'],
                              "{#MATCHINGRULE}" : "Unknown Rule",
                              "{#ATTACKID}" : one_attack_row['attackIpsId'], 
                              "{#ATTACKSTATUS}" : attack_status }
            if self.debug:
                print 'DBG:DDALERT:%s:single_alert:%s:' % (local_method,
                                                        single_alert) 
            new_alert_list.append(single_alert)
        if self.debug:
            print 'DBG:DDALERT:%s:Return new_alert_list to caller' % (
                                                        local_method)
            print 'DBG:DDALERT:%s:END' % (local_method)
        return new_alert_list                      


###############################################################################

def parse_cli():
    ''' CLI parser using OptionParser'''

    parser = OptionParser()
    parser.add_option('-d', '--debug',
                      dest='debug',
                      default=False,
                      help='Enable debug output',
                      action='store_true')
    parser.add_option('-c', '--config',
                      dest='config',
                      default=None,
                      help='Configuration file location override',
                      type='string',
                      action='store')
    return parser.parse_args()

###############################################################################


def main():
    '''  Main executable routine.  Enforce options and call routines. 
         Start by pulling the list of current attacks from Radware Vision 
         console.  If there are no current attacks, return nothing and exit 
         successfully.
    '''

    (options, args) = parse_cli()

    if options.debug:
        local_method = sys._getframe().f_code.co_name
        print 'DBG:DDALERT:BEGIN:', local_method

    dd_alert = DDALERT(options)
    if not dd_alert.get_attack_list():
        exit(0)

    new_alert_list = []
    new_alert_list = dd_alert.get_new_alerts()

    data = { "data" : new_alert_list }
    json_data = json.dumps(data)
    print json_data
    exit(0)

if __name__ == '__main__':
    main()
