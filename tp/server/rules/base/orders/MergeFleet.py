
import copy
from config import netlib

from sbases.SQL import NoSuch
from sbases.Object import Object
from sbases.Order import Order
from sbases.Message import Message

from sobjects.Fleet import Fleet

class MergeFleet(Order):
	"""\
Merge two fleets together.
"""

	attributes = {\
		'fleet': Order.Attribute("fleet", {}, 'protected', type=netlib.objects.constants.ARG_OBJECT, 
				desc="Fleet to merge with.")
	}
	
	def do(self):
		# We need the original fleet
		fleet1 = Object(self.oid)
		
		# We need the other fleet
		if self.fleet != -1:
			fleet2 = Object(self.fleet)

		message = Message()
		message.slot = 0
		message.bid = fleet1.owner
		message.subject = "Merge Fleet failed."
		
		# Check the other object is actually a fleet...
		if self.fleet == -1 or fleet2.type != 'sobjects.Fleet':
			# Send message about the owner not matching...
			message.body = """\
The merge failed (of %s) because the merge target wasn't a fleet!
The merge order has been removed.
""" % (fleet1.name)
			message.insert()
			
			self.remove()
			return

		# Check they have the same owner :)
		if fleet1.owner != fleet2.owner:
			# Send message about the owner not matching...
			message.body = """\
The merge between %s and %s failed because you didn't own both fleets.
The merge order has been removed.
""" % (fleet1.name, fleet2.name)
			message.insert()
			
			self.remove()
			return
		
		# Check they are at the same position
		if (fleet1.posx, fleet1.posy, fleet1.posz) != (fleet2.posx, fleet2.posy, fleet2.posz):
			return

		# Merge the fleets
		for type, number in fleet1.ships.items():
			if fleet2.ships.has_key(type):
				fleet2.ships[type] += number
			else:
				fleet2.ships[type] = number
				
			del fleet1.ships[type]

		fleet1.save()
		# Remove the other fleet
		fleet2.remove()

		self.remove()

	def turns(self, turns=0):
		return turns+1

	def resources(self):
		return []

	def fn_fleet(self, value=None):
		if value == None:
			return self.fleet
		else:
			try:
				fleet = Object(value)
				if fleet.type != 'sobjects.Fleet':
					self.fleet = -1
				else:
					self.fleet = value
			except NoSuch:
				self.fleet = -1

			return 
			
MergeFleet.typeno = 4
Order.types[MergeFleet.typeno] = MergeFleet
