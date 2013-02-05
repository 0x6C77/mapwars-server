#!/usr/bin/env python


import socket
import sys
import time

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

sock.send('{"action":"login","user":"rabbit","pass":"pass"}')
print sock.recv(1024)
time.sleep(3)
sock.send('{"action":"update","user":"rabbit"}')
print sock.recv(1024)

sock.close()

sys.exit(0)
