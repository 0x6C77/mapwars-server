#!/usr/bin/env python


import socket
import sys

HOST = 'localhost'
PORT = 4565

try:
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
	sys.stderr.write("[ERROR] %s\n" % msg[1])
	sys.exit(1)

try:
	sock.connect((HOST, PORT))
except socket.error, msg:
	sys.stderr.write("[ERROR] %s\n" % msg[1])
	sys.exit(2)

sock.send('{"action":"login","user":"dog","pass":"pass"}')
print sock.recv(1024)

sock.send('{"action":"location","user":"dog","lat":"52.35198423091655","lon":"-1.9664990901947021"}')
print sock.recv(1024)

sock.send('{"action":"unit.create","user":"dog","lat":"52.352164445438646","lon":"-1.9658446311950684"}')
print sock.recv(1024)

sock.send('{"action":"unit.move","user":"dog","id":"1","lat":"52.4126275","lon":"-4.0675783"}')
print sock.recv(1024)

sock.close()

sys.exit(0)
