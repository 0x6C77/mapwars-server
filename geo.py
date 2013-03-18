print "Loaded geo class..."
import math

class Geo:
    @staticmethod
    def boundingBox(location, half_side_in_miles):
        half_side_in_km = half_side_in_miles * 1.609344
        lat = math.radians(location['lat'])
        lon = math.radians(location['lon'])

        radius  = 6371
        # Radius of the parallel at given latitude
        parallel_radius = radius*math.cos(lat)

        lat_min = lat - half_side_in_km/radius
        lat_max = lat + half_side_in_km/radius
        lon_min = lon - half_side_in_km/parallel_radius
        lon_max = lon + half_side_in_km/parallel_radius
        rad2deg = math.degrees

        return dict(latMin=rad2deg(lat_min), lonMin=rad2deg(lon_min), latMax=rad2deg(lat_max), lonMax=rad2deg(lon_max))

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