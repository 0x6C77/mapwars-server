from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
import json
import time
import web

#user class
from user import User
from vehicle import Vehicle
from defence import Defence

## CONSTANTS
PORT = 4565;


class Connection(Protocol):
	def connectionMade(self):
		log("New connection")
		self.factory.clients.append(self)

	def connectionLost(self, reason):
		log("Lost connection")
		self.factory.clients.remove(self)

	def dataReceived(self, data):
		data = json.loads(data)
		user = data['user']
		action = data['action']
		replyDic = dict(action=action)

		#check if user is logged in or attempting to login
		if action != "login" and user not in self.factory.users:
			replyDic['response'] = 0
			reply = json.dumps(replyDic)
			self.transport.write(reply + '\n')
			return			

		if action == "login":
			replyDic['user'] = user
			if data['pass'] == "pass":

				# check if user object exists
				if user not in self.factory.users:
					# create user
					self.factory.id += 1

					tmp = User(self.factory.id, user)
					self.factory.users[user] = tmp

				# create json reply
				replyDic['response'] = 1
				reply = json.dumps(replyDic)
				self.transport.write(reply + '\n')
				log("[{0}] [{1}] Login".format(getTime(), user))
			else:
				replyDic['response'] = 0
				reply = json.dumps(replyDic)
				self.transport.write(reply + '\n')
		elif action == "location":
			# store location
			location = dict()
			location['lat'] = data['lat']
			location['lon'] = data['lon']
			user = data['user']
			self.factory.locations[user] = location

			self.factory.users[user].set_location(location['lat'], location['lon'])

			log("[{0}] [{1}] Location - {2}, {3}".format(getTime(), user, location['lat'], location['lon']))

			# respond with all vehicle details
			replyDic['units'] = []
			for k, u in self.factory.users.iteritems():
				vehicles = u.get_units()
				for vehicle in vehicles:
					tmpDic = vehicle.get_details()
					tmpDic['user'] = u.user
					replyDic['units'].append(json.dumps(tmpDic))
			reply = json.dumps(replyDic)
			self.transport.write(reply + '\n')
		elif action == "unit.create":
			user = data['user']
			lat = data['lat']
			lon = data['lon']
			typ = data['type']

			if (typ == 'VEHICLE'):
				self.factory.unit_id += 1
				tmp_vehicle = Vehicle(self.factory.unit_id, typ)
				tmp_vehicle.set_location(lat, lon)
				self.factory.users[user].add_unit(tmp_vehicle)
			elif (typ == 'DEFENCE'):
				self.factory.unit_id += 1
				tmp_defence = Defence(self.factory.unit_id, typ)
				tmp_defence.set_location(lat, lon)
				self.factory.users[user].add_unit(tmp_defence)

			replyDic['status'] = 1
			replyDic['id'] = self.factory.unit_id

			# respond with all vehicle details
			replyDic['units'] = []
			for k, u in self.factory.users.iteritems():
				units = u.get_units()
				for unit in units:
					tmpDic = unit.get_details()
					tmpDic['user'] = u.user
					replyDic['units'].append(tmpDic)

			reply = json.dumps(replyDic)


			# send to all connected clients
			for client in self.factory.clients:
				client.transport.write(reply + '\n')


			log("[{0}] [{1}] Created {2} {3} - {4}, {5}".format(getTime(), user, typ, self.factory.unit_id, lat, lon))
		elif action == "unit.move":
			user = data['user']
			id = data['id']
			lat = data['lat']
			lon = data['lon']

			tmp_vehicle = self.factory.users[user].get_unit(id)
			if tmp_vehicle == 0:
				replyDic['status'] = 0

				reply = json.dumps(replyDic)
				self.transport.write(reply + '\n')
			else:
				tmp_vehicle.set_location(lat, lon)

				replyDic['status'] = 1

				# respond with all vehicle details
				replyDic['units'] = []
				for k, u in self.factory.users.iteritems():
					vehicles = u.get_units()
					for vehicle in vehicles:
						tmpDic = vehicle.get_details()
						tmpDic['user'] = u.user
						replyDic['units'].append(tmpDic)

				reply = json.dumps(replyDic)

			# send to all connected clients
			for client in self.factory.clients:
				client.transport.write(reply + '\n')

			log("[{0}] [{1}] Moved vehicle {2} - {3}, {4}".format(getTime(), user, id, lat, lon))
			

def getTime():
	return time.strftime("%I:%M:%S", time.localtime())

def log(str):
	logfile = open("log", "a")
	logfile.write(str + "\n")
	print(str)

f = Factory()
f.protocol = Connection
f.clients = []
f.locations = dict()
f.users = dict()

#temporary id
f.id = 0;
f.unit_id = 0;

reactor.listenTCP(PORT, f)
log("Server started, port {0}\n".format(PORT))
reactor.run()
