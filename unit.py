print "Loaded unit class..."

class Unit:
	def __init__(self, id, type):
		self.id = id
		self.type = type

	def set_location(self, lat, lon):
		self.lat = lat
		self.lon = lon

	def set_target_location(self, lat, lon):
		self.targetLat = lat
		self.targetLon = lon

	def get_details(self):
		replyDic = dict(id=self.id)
		replyDic['type'] = self.type
		replyDic['lat'] = self.lat
		replyDic['lon'] = self.lon
		return replyDic
