print "Loaded control class..."
import time
import threading
import sqlite3 as lite
import random
from geo import Geo

class Control(threading.Thread):
    def run(self):
        lastFired = dict()

        sql = lite.connect('db.sqlite')
        db = sql.cursor()
        db.row_factory = lite.Row
        while True:
            db.execute("SELECT * FROM units WHERE health > 0 AND lat != target_lat OR lon != target_lon")
            data = db.fetchall()
            for unit in data:
                lat1 = unit['lat']
                lon1 = unit['lon']
                lat2 = unit['target_lat']
                lon2 = unit['target_lon']
                unitID = unit['unit_id']

                distance = Geo.distance(dict(lat=lat1, lon=lon1), dict(lat=lat2, lon=lon2))

                steps = round(distance / 4);

                if steps >= 1:
                    lat1 = lat1 + ((lat2 - lat1) / steps)
                    lon1 = lon1 + ((lon2 - lon1) / steps)
                else:
                    lat1 = lat2
                    lon1 = lon2

                db.execute("UPDATE units SET lat = ?, lon = ? WHERE unit_id = ?", (lat1, lon1, unitID))

            #random gives each unit a chance to fire first
            db.execute("SELECT * FROM units WHERE health > 0 ORDER BY RANDOM()")
            data = db.fetchall()
            for unit in data:
                t = int(round(time.time() * 1000))

                lat1 = unit['lat']
                lon1 = unit['lon']
                unitID = unit['unit_id']
                userID = unit['user_id']

                if unitID in lastFired and t - lastFired[unitID] < 500:
                    continue

                #randomize firing
                if random.randint(1, 5) != 1:
                    continue

                #get closest enemy unit within range of weapons
                bBox = Geo.boundingBox(dict(lat=lat1, lon=lon1), 0.10)

                db.execute("SELECT * FROM units WHERE user_id != ? AND health > 0 AND lat > ? AND lat < ? AND lon > ? AND lon < ? LIMIT 1", (userID, bBox['latMin'], bBox['latMax'], bBox['lonMin'], bBox['lonMax']))
                target = db.fetchone()
                if target is not None:
                    dis = Geo.distance(dict(lat=lat1, lon=lon1), dict(lat=target['lat'], lon=target['lon']))
                    if dis < 100:
                        lastFired[unitID] = t
                        targetID = target['unit_id']

                        db.execute("UPDATE units SET health = health - 10 WHERE unit_id = ?", (targetID,))

                        print "{0} shot {1} ({2})".format(unitID, targetID, (int(target['health']) - 10))

            sql.commit()
            time.sleep(0.2)