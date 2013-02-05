print "Loaded user class..."

class User:
	def __init__(self, id, user):
		self.id = id
		self.user = user
		self.units = []
		print "{0} - {1}".format(id, user)

	def set_location(self, lat, lon):
		self.lat = lat
		self.lon = lon

	def add_unit(self, unit):
		self.units.append(unit)

	def get_units(self):
		return self.units

	def get_unit(self, id):
		for unit in self.units:
			if int(unit.id) == int(id):
				return unit			

		return 0
