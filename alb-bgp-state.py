#!/usr/bin/python

import sys
import signal
import os
import socket
from jsonrpclib import Server

timeout=29
socket.setdefaulttimeout(timeout)

def deadlinehandler(signum, frame):
    print "2"
    exit(2)
def main():
    try:
        switch = Server( "http://localhost:8080/command-api" )
        response = switch.runCmds( 1, [ "show ip bgp summary" ] )
        peer =  response[0][ "vrfs" ]["default"]["peers"]
        peer_key =  peer.keys()
        peer =  response[0][ "vrfs" ]["default"]["peers"][peer_key[0]]["peerState"]
        if peer == "Established" :
            print "0"
        else:
            print "1"
    except:
        deadlinehandler(2,3)
    exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGALRM, deadlinehandler)
    signal.alarm(timeout)
    main()
    signal.alarm(0)
