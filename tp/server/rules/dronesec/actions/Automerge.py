from tp.server.bases.Object import Object
from tp.server.rules.dronesec.objects.Fleet import Fleet
from tp.server.utils import WalkUniverse
from tp.server.bases.Message import Message
from tp.server.rules.dronesec.bases.Drone import Drone

def do(top):

	#Get all Fleets
	def h(obj, d):
		# Check the object can go into combat
		if not obj.type.endswith('objects.Fleet'):
			return

		# Check the object isn't owned by the universe
		if obj.owner == -1:
			return

		pos = obj.posx, obj.posy, obj.posz
		if not d.has_key(pos):
			d[pos] = []

		d[pos].append(obj)

	d = {}
	WalkUniverse(top, "before", h, d)

	for pos, fleets in d.items():
		for obj in fleets:
			fleetsDone = []
#			for f in fleets:
			# check: Make sure the ship isn't merging with another player's
			for fleet in fleets:
				if fleet.owner == obj.owner:
				#Make sure that the keys are the same (same types)
				#also makes sure that the ship isn't trying to merge with itself
					if fleet.ships.keys() == obj.ships.keys() and fleet.id != obj.id:
						# Merge the fleets have the same type of ships
						for type, number in fleet.ships.items():
							if obj.ships.has_key(type):
								obj.ships[type] += number
								fleet.ships[type] -= number
								print "Merging %s's %s with %s" % (obj.id, Drone(type).name, fleet.id)
								# Send a message to the owner that the fleet has merged...
								message = Message()
								message.bid = obj.owner
								message.slot = -1
								message.subject = "Automatic Merging complete."
								message.body = """%s has merged with %s at (%i, %i, %i).""" % \
									(obj.name, fleet.name, obj.posx, obj.posy, obj.posz)
								message.insert()
						fleetsDone.append(fleet)
						fleet.save()
			for fleet in fleetsDone:
				fleets.remove(fleet)
			obj.save()