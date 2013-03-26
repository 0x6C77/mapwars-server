print "Loaded user class..."

class User:
	def __init__(self, id, connection):
		self.id = id
		self.connection = connection

	def set_location(self, lat, lon):
		self.lat = lat
		self.lon = lon

	def get_location(self):
		return dict(lat=self.lat, lon=self.lon)

	def set_connection(self, connection):
		self.connection = connection

	def get_connection(self):
		return self.connection
