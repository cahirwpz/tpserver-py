"""\
Captures a Planet
"""

from tp.server.bases.Object import Object
from tp.server.bases.Order import Order
from tp.server.utils import WalkUniverse
from tp.server.rules.dronesec.bases.Drone import Drone

from tp.server.rules.dronesec.research.ResearchCalculator import ResearchCalculator as RC

from tp.server.bases.Message import Message

def do(top):
	def h(obj):
		if obj.type.endswith("Planet"):
			#Build list of fleets that could capture the planet
			capturers = Object.bypos([obj.posx, obj.posy, obj.posz], size=obj.size+2)
			capturers  = [id for (id, time) in capturers if Object(id).type ==
				'tp.server.rules.dronesec.objects.Fleet']
			#If there are any capturers present.
			if capturers:
				checkOwners = dict()
				#Checks to see how many players are at the planet and their total power
				for id in capturers:
					if hasattr(Object(id), 'target'):
						i = Object(id).owner
						power = Object(id).calcPower()
						try:
							checkOwners[i] += power
						except:
							checkOwners[i] = power
				#A conqueror is the only person with a chance to capture a planet.
				#A conqueror is the player with the most power at the planet
				conqueror = max(checkOwners,key = lambda a: checkOwners.get(a))
				conqpow = checkOwners[conqueror]
				#Conquerors should not already own the planet
				if conqueror != obj.owner:
					if len(checkOwners) > 1:
						for id, pow in checkOwners.items():
							if id != conqueror:
								conqpow -= pow
					# To Capture a planet a conqueror must have 50 power more
					# than all other players at that planet
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
							# This should go through the fleets taking away the
							# ships with the smallest amount of power first.
							if powerLoss < 50:
								drone = Object(id)
								if drone.owner == conqueror and hasattr(drone, 'target'):
									types = dict()
									for ship in drone.ships.keys():
										power, s, sr = RC.World(conqueror, ship)
										
										types[ship] = power
										removed = min(types,key = lambda a: types.get(a))
										while powerLoss < 50 and drone.ships[ship] > 0:
											powerLoss += power
											drone.ships[ship] -= 1
										drone.tidy()
										drone.save()
									
									#Remove Orders from the planet
									while obj.orders():
										o = Order(Order.realid(object.id, 0))
										o.remove()
										o.save()
				obj.save()
	WalkUniverse(top, "before", h)
