print "Loaded geo class..."
import math

class Geo:
    def boundingBox(self, location, half_side_in_miles):
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