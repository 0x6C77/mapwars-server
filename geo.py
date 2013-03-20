print "Loaded geo class..."
import math
from decimal import Decimal

class Geo:
    @staticmethod
    def boundingBox(location, radius_km):
        deg2rad = math.radians
        rad2deg = math.degrees

        radDist = radius_km / 6371.0
        radLat = deg2rad(location['lat'])
        radLon = deg2rad(location['lon'])

        minLat = radLat - radDist
        maxLat = radLat + radDist

        deltaLon = math.asin(math.sin(radDist) / math.cos(radLat))
        minLon = radLon - deltaLon
        maxLon = radLon + deltaLon
        
        return dict(latMin=rad2deg(minLat), lonMin=rad2deg(minLon), latMax=rad2deg(maxLat), lonMax=rad2deg(maxLon))


    # returns distance in between two loctaions
    @staticmethod
    def distance(location1, location2):
        rad2deg = math.degrees
        deg2rad = math.radians

        lat1 = location1['lat']
        lat2 = location2['lat']
        lon1 = location1['lon']
        lon2 = location2['lon']

        theta = lon1 - lon2
        dist = math.sin(deg2rad(lat1)) * math.sin(deg2rad(lat2)) + math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * math.cos(deg2rad(theta));

        dist = math.acos(dist);
        dist = rad2deg(dist);
        dist = dist * 60 * 1.852 * 1000;

        return dist