#!/usr/bin/env python
import socket
import sys
import time
import re
import json


HOST = 'localhost'
PORT = 4565

sess = None
userID = None

try:
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((HOST, PORT))
except socket.error, msg:
	sys.stderr.write("[ERROR] %s\n" % msg[1])
	sys.exit(1)


while True:
	n = raw_input("> ")

	msgDic = dict()

	if n == "exit":
		break  # stops the loop
	else:
		match = re.findall("[^\s]+", n, re.M|re.I)
		if match:
			if match[0] == 'login':
				msgDic['action'] = "user.login"
				msgDic['user'] = match[1]
				msgDic['pass'] = match[2]
			elif match[0] == 'register':
				msgDic['action'] = "user.register"
				msgDic['user'] = match[1]
				msgDic['pass'] = match[2]
				msgDic['email'] = match[3]
			elif match[0] == 'location':
				msgDic['action'] = "user.location"
				msgDic['lat'] = match[1]
				msgDic['lon'] = match[2]
			elif match[0] == 'unit':
				msgDic['action'] = "unit.create"
				msgDic['type'] = match[1]
				msgDic['lat'] = match[2]
				msgDic['lon'] = match[3]
			elif match[0] == 'move':
				msgDic['action'] = "unit.move"
				msgDic['id'] = match[1]
				msgDic['lat'] = match[2]
				msgDic['lon'] = match[3]
			else:
				continue
			
			if sess:
				msgDic['sess'] = sess
			if userID:
				msgDic['userID'] = userID

			msg = json.dumps(msgDic)
			print '\x1b[38;5;15m' + "S " + msg + '\033[0m'
			sock.send(msg)


		else:
			continue


	rec = sock.recv(2048)
	data = json.loads(rec)

	#check for session data
	if data['action'] == 'user.login' and data['status'] == 1:
		sess = data['sess']
		#sess = 'cat'
		userID = data['userID']

	if data['status'] == 1:
		print '\x1b[38;5;46m' + "R " + rec + '\033[0m'
	else:
		print '\x1b[38;5;160m' + "R " + rec + '\033[0m'

sock.close()

sys.exit(0)
