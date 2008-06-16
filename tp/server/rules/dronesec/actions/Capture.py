"""\
Captures a Planet
"""

from tp.server.bases.Object import Object
from tp.server.utils import WalkUniverse
from tp.server.rules.dronesec.objects.Planet import Planet
from tp.server.rules.dronesec.objects.Fleet import Fleet as Drone
from tp.server.bases.Message import Message

def do(top):
	def h(obj):
		if obj.type.endswith("Planet"):
			capturers = Object.bypos([obj.posx, obj.posy, obj.posz], size=obj.size+2)
			capturers  = [id for (id, time) in capturers if Object(id).type ==
				'tp.server.rules.dronesec.objects.Fleet']
			if capturers:
				checkOwners = dict()
				for id in capturers:
					if hasattr(Object(id), 'target'):
						i = Object(id).owner
						power = Object(id).calcPower()
						try:
							checkOwners[i] += power
						except:
							checkOwners[i] = power
				conqueror = max(checkOwners,key = lambda a: checkOwners.get(a))
				conqpow = checkOwners[conqueror]
				if conqueror != obj.owner:
					if len(checkOwners) > 1:
						for id, pow in checkOwners:
							if id != conqueror:
								conqpow -= pow
					if conqpow >= 50:
						obj.owner = conqueror
						#Message
						message = Message()
						message.slot = -1
						message.bid = conqueror
						print "Capture of Planet %s (%s) (by %s) succeeded." % (obj.id, obj.name, conqueror)
						message.subject = "Planet Captured."
						message.body = """\
Capture of %s <b>succeded</b>.""" % (obj.name,)
						message.insert()

						#remove Drones
						powerLoss = 0
						for id in capturers:
							if powerLoss < 50:
								drone = Object(id)
								if drone.owner == conqueror and hasattr(drone, 'target'):
									types = dict()
									for ship in drone.ships.keys():
										types[ship] = drone.ship_power[ship]
										removed = min(types,key = lambda a: types.get(a))
										while powerLoss < 50 and drone.ships[ship] > 0:
											powerLoss += drone.ship_power[ship]
											drone.ships[ship] -= 1
										drone.tidy()
										drone.save()
				obj.save()
	WalkUniverse(top, "before", h)