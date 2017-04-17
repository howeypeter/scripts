#!/usr/bin/python
# quick script to download a day's worth of logs
import boto
import boto.s3.connection
access_key = ''
secret_key = ''

conn = boto.connect_s3(
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        host = 's3-us-west-1.amazonaws.com',
        #is_secure=False,               # uncomment if you are not using ssl
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
        )

bucket = conn.get_bucket('sfly-prod-cdn')
for key in bucket.list():
        print "{name}".format(
                name = key.name,
                )

for key in bucket.list():
       print "{name}".format(
                name = key.name,
                )
       if "2017-04-11" in key.name :
        key = bucket.get_key(key.name)
        key.get_contents_to_filename(key.name)
