
import math
from config import netlib

from sbases.Order import Order
from sbases.Object import Object
from sbases.Message import Message

Frigate = 1

class Colonise(Order):
	"""\
Colonise the planet this fleet is orbiting. Will use one frigate class ship.
"""

	attributes = {\
	}
	
	def do(self):
		# We are going to have to modify the object so lets load it
		fleet = Object(self.oid)
		planet = Object(fleet.parent)

		# Do checks :)
		message = Message()
		message.slot = -1
		message.bid = fleet.owner
		message.subject = "Colonise failed."
		
		if planet.type != 'sobjects.Planet':
			message.body = """\
Colonise of %s <b>failed</b> because %s is not a Planet!<br>
The order has been removed.""" % (planet.name, planet.name)
			message.insert()

			self.remove()
			return

		if planet.owner != 0:
			message.body = """\
Colonise of %s <b>failed</b> because %s is already colonised by %s!<br>
You can decolonised the planet by bombing the bejesus out of it.
The order has been removed.""" % (planet.name, planet.owner)
			message.insert()

			self.remove()
			return

			

		if not fleet.ships.has_key(Frigate) or fleet.ships[Frigate] < 1:
			message.body = """\
Colonise of %s <b>failed</b> because %s does not have any Frigates!<br>
The order has been removed.""" % (planet.name, fleet.name)
			message.insert()

			self.remove()
			return

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

Colonise.typeno = 5
Colonise.types[Colonise.typeno] = Colonise
