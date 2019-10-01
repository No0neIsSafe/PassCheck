#!/usr/bin/python

import json
import sys

if len(sys.argv) < 2:
	print "Usage: ./parser.py <FILENAME>"
	sys.exit(1)

filename = sys.argv[1]
output = open('creds_'+filename+'.txt', 'a+')
with open(filename) as json_file:
	data = json.load(json_file)
	#print data["49511562"]["email"]
	for i in data:
		email = data[i]["email"]
		passw = data[i]["passw"]
		output.write(email+":"+passw+'\n')
