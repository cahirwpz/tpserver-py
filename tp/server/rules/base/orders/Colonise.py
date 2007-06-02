
import math
from tp import netlib

from tp.server.bases.Order import Order
from tp.server.bases.Object import Object
from tp.server.bases.Message import Message

Frigate = 1

class Colonise(Order):
	"""\
Colonise the planet this fleet is orbiting. Will use one frigate class ship.
"""
	typeno = 5

	attributes = {\
		'target': Order.Attribute("target", -1, 'public', type=netlib.objects.constants.ARG_OBJECT, 
					desc="ID of object to colonise."),
	}
	
	def do(self):
		# We are going to have to modify the object so lets load it
		fleet = Object(self.oid)
		planet = Object(self.target)

		# Do checks :)
		message = Message()
		message.slot = -1
		message.bid = fleet.owner
		message.subject = "Colonise failed."

		if planet.posx != fleet.posx or planet.posy != fleet.posy or planet.posz != planet.posz:
			print "Colonise of Planet %s (%s) (by %s-%s) failed. The fleet was not orbiting the planet!" % (planet.id, planet.name, fleet.id, fleet.name)
			message.body = """\
Colonise of %s <b>failed</b> because %s was not orbiting the planet.<br>
The order has been removed.""" % (planet.name, fleet.name)
			message.insert()

			self.remove()
			return	
	
		if not planet.type.endswith('Planet'):
			print "Colonise of Planet %s (%s) (by %s-%s) failed. %s not a planet!" % (planet.id, planet.name, fleet.id, fleet.name, planet.name)
			message.body = """\
Colonise of %s <b>failed</b> because %s is not a Planet!<br>
The order has been removed.""" % (planet.name, planet.name)
			message.insert()

			self.remove()
			return

		if not planet.owner in (-1, 0):
			print "Colonise of Planet %s (%s) (by %s-%s) failed. %s is owned by %s." % (planet.id, planet.name, fleet.id, fleet.name, planet.name, planet.owner)
			message.body = """\
Colonise of %s <b>failed</b> because %s is already colonised by %s!<br>
You can decolonised the planet by bombing the bejesus out of it.
The order has been removed.""" % (planet.name, planet.name, planet.owner)
			message.insert()

			self.remove()
			return

		if not fleet.ships.has_key(Frigate) or fleet.ships[Frigate] < 1:
			print "Colonise of Planet %s (%s) (by %s-%s) failed. %s has no frigates." % (planet.id, planet.name, fleet.id, fleet.name, fleet.name)
			message.body = """\
Colonise of %s <b>failed</b> because %s does not have any Frigates!<br>
The order has been removed.""" % (planet.name, fleet.name)
			message.insert()

			self.remove()
			return

		print "Colonise of Planet %s (%s) (by %s-%s) succeeded." % (planet.id, planet.name, fleet.id, fleet.name)
		message.subject = "Colonise success."
		message.body = """\
Colonisation of %s <b>succeded</b>.""" % (planet.name,)
		message.insert()
		
		planet.owner = fleet.owner
		fleet.ships[Frigate] -= 1

		planet.save()
		fleet.save()

		self.remove()

	def turns(self, turns=0):
		return 1 + turns

	def resources(self):
		return []
