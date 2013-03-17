from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
import json
import time
import web
import uuid
import sqlite3 as lite

#user class
from user import User
from geo import Geo

## CONSTANTS
PORT = 4565;



class Server(Protocol):
	global db, sql
	sql = lite.connect('db.sqlite')
	db = sql.cursor()
	# change results to dicts
	db.row_factory = lite.Row

	def __init__(self, factory):
		self.factory = factory

	def connectionMade(self):
		log("New connection")
		self.factory.clients.append(self)

	def connectionLost(self, reason):
		log("Lost connection")
		self.factory.clients.remove(self)

	def dataReceived(self, data):
		try:
			data = json.loads(data)
		except ValueError:
			replyDic['status'] = 0
			reply = json.dumps(replyDic)
			self.transport.write(reply + '\n')
			return

		action = data['action']
		replyDic = dict(action=action)

		#check if user is logged in or attempting to login
		if action != "user.login" and action != "user.register":
			userID = data['userID']
			sess = data['sess']
			#lookup session id
			if userID not in self.factory.users or self.factory.users[userID].sess != sess:
				replyDic['status'] = 0
				replyDic['response'] = 'Invalid session'
				reply = json.dumps(replyDic)
				self.transport.write(reply + '\n')
				return

			#get user object
			user = self.factory.users[userID]

		if action == "user.login":
			user = data['user']
			password = data['pass']

			db.execute("SELECT user_id FROM users WHERE username = ? AND password = ?", (user,password))
			data = db.fetchone()

			if data is not None:
				userID = data['user_id']
				replyDic['userID'] = userID

				# check if user object exists
				if userID not in self.factory.users:
					tmp = User(userID, user)
					self.factory.users[userID] = tmp

				#update record
				replyDic['sess'] = str(uuid.uuid4())
				self.factory.users[userID].sess = replyDic['sess']

				replyDic['status'] = 1
				reply = json.dumps(replyDic)
				self.transport.write(reply + '\n')
				log("[{0}] [{1}] Login".format(getTime(), user))
			else:
				replyDic['status'] = 0
				reply = json.dumps(replyDic)
				self.transport.write(reply + '\n')
		elif action == "user.register":
			user = data['user']
			password = data['pass']
			email = data['email']
			try:
				db.execute("INSERT INTO users (username, password, email) VALUES (?,?,?)", (user,password,email))
				sql.commit()
				replyDic['status'] = 1
			except lite.Error, e:
				replyDic['status'] = 0

			reply = json.dumps(replyDic)
			self.transport.write(reply + '\n')
		elif action == "user.location":
			# store location
			location = dict()
			location['lat'] = float(data['lat'])
			location['lon'] = float(data['lon'])

			user.set_location(location['lat'], location['lon'])

			log("[{0}] [{1}] Location - {2}, {3}".format(getTime(), user.user, location['lat'], location['lon']))

			replyDic['status'] = 1

			# respond with all vehicle details
			replyDic['units'] = self.getUnitList(user.get_location())

			reply = json.dumps(replyDic)
			self.transport.write(reply + '\n')
		elif action == "unit.create":
			lat = data['lat']
			lon = data['lon']
			typ = data['type']

			#insert unit into DB and get unit id
			try:
				db.execute("INSERT INTO units (user_id, type, lat, lon) VALUES (?,?,?,?)", (userID,typ,lat,lon))
				sql.commit()
				unitID = db.lastrowid
			except lite.Error, e:
				replyDic['status'] = 0	
				client.transport.write(reply + '\n')
				return

			replyDic['status'] = 1
			replyDic['unitID'] = unitID

			# respond with all units details
			replyDic['units'] = self.getUnitList(user.get_location())

			reply = json.dumps(replyDic)


			# send to all connected clients
			for client in self.factory.clients:
				client.transport.write(reply + '\n')


			log("[{0}] [{1}] Created {2} {3} - {4}, {5}".format(getTime(), userID, typ, unitID, lat, lon))
		elif action == "unit.move":
			unitID = data['id']
			lat = data['lat']
			lon = data['lon']

			db.execute("SELECT unit_id FROM units WHERE unit_id = ? AND user_id = ?", (unitID,userID))
			res = db.fetchone()
			print res

			if res is None:
				replyDic['status'] = 0
				reply = json.dumps(replyDic)
				self.transport.write(reply + '\n')
				return

			# update db
			db.execute("UPDATE units SET lat = ?, lon = ? WHERE unit_id = ? AND user_id = ?", (lat, lon, unitID, userID))
			sql.commit()

			replyDic['status'] = 1
			replyDic['units'] = self.getUnitList(user.get_location())
			reply = json.dumps(replyDic)

			# send to all connected clients
			for client in self.factory.clients:
				client.transport.write(reply + '\n')

			log("[{0}] [{1}] Moved vehicle {2} - {3}, {4}".format(getTime(), userID, unitID, lat, lon))
	
	def getUnitList(self, location):
		reply = []

		bBox = geo.boundingBox(location, 25)

		db.execute("SELECT * FROM units WHERE lat > ? AND lat < ? AND lon > ? AND lon < ?", (bBox['latMin'], bBox['latMax'], bBox['lonMin'], bBox['latMax']))
		data = db.fetchall()

		for unit in data:
			tmpDic = dict()
			tmpDic['unitID'] = unit['unit_id']
			tmpDic['userID'] = unit['user_id']
			tmpDic['type'] = unit['type']
			tmpDic['lat'] = unit['lat']
			tmpDic['lon'] = unit['lon']
			tmpDic['health'] = unit['health']
			reply.append(tmpDic)

		return reply



class ServerFactory(Factory):
    def __init__(self):
		self.clients = []
		self.users = dict()
		self.unit_id = 0

    def buildProtocol(self, addr):
        return Server(self)


def getTime():
	return time.strftime("%I:%M:%S", time.localtime())

def log(str):
	logfile = open("log", "a")
	logfile.write(str + "\n")
	print(str)


def main():
	reactor.listenTCP(PORT, ServerFactory())
	log("Server started, port {0}\n".format(PORT))
	reactor.run()

if __name__ == '__main__':
	global geo
	geo = Geo()
	main();
