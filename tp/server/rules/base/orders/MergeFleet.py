
import copy
import netlib

from sbases.Object import Object
from sbases.Order import Order
from sbases.Message import Message

from sobjects.Fleet import Fleet

class MergeFleet(Order):
	"""\
Merge two fleets together.
"""

	attributes = {\
		'fleet': Order.Attribute("fleet", {}, 'protected', type=netlib.objects.Constants.ARG_OBJ, 
				desc="Fleet to merge with.")
	}
	
	def do(self):
		# We need the original fleet
		fleet1 = Object(self.oid)
		# We need the other fleet
		fleet2 = Object(self.fleet)

		# Check they are at the same position

		# Merge the fleets
		for type, number in fleet1.ships.items():
			if fleet2.ships.has_key(type):
				fleet2.ships[type] += number
			else:
				fleet2.ships[type] = number
				
			del fleet1.ships[type]

		self.remove()

	def turns(self, turns=0):
		return self.turns+1

	def resources(self):
		return []

	def fn_fleet(self, value=None):
		if value == None:
			return returns, self.ships.items()
		else:
			pass

MergeFleet.typeno = 4
Order.types[MergeFleet.typeno] = MergeFleet
