#!/bin/bash
#
# list.txt contains a list of URLs to be cached.
# vip.txt lists a series of IPs (nodes) to be cached.
# use IPs rather than DNS to avoid DNS lookups.
# logs output to precache-result.txt
# 1 byte range request will trigger a full file download.
#
FILELIST="topurls1.txt"

echo "" > precache-result.txt
for VIP in $(echo "23.72.120.88 23.72.105.64")
do 
echo VIP $VIP >> precache-result.txt
        for URL in $( head $FILELIST | awk '{print $2}')
        do
        echo $URL >> precache-result.txt
        echo $URL | xargs -t -n 1 -P 8 curl -o /dev/null -r 0-1 -x $VIP:80 2>&1 >> precache-result.txt
        sleep 1
        done
done
