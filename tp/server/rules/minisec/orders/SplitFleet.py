
import copy
from tp import netlib

from tp.server.bases.Object import Object
from tp.server.bases.Order import Order
from tp.server.bases.Message import Message

from tp.server.rules.minisec.objects.Fleet import Fleet

class SplitFleet(Order):
	"""\
Split some ships into a new fleet.
"""
	typeno = 3

	attributes = {\
		'call': Order.Attribute("call", "New Fleet", 'protected', type=7, #netlib.objects.constants.ARG_STRING, 
				desc="What to call the new fleet."),
		'ships': Order.Attribute("ships", {}, 'protected', type=6, #netlib.objects.constants.ARG_LIST, 
				desc="Ships to move into new fleet.")
	}
	
	def do(self):
		# We need the original fleet
		fleet1 = Object(self.oid)
		
		# Create the new fleet
		fleet2 = copy.deepcopy(fleet1)
		fleet2.name = self.call
		fleet2.ships = {}

		# Add the ships to the new fleet
		for type, number in self.ships:
			if fleet1.ships[type] - number > 0:
				fleet1.ships[type] -= number
				fleet2.ships[type] = number
			else:
				fleet2.ships[type] = fleet1.ships[type]
				fleet1.ships[type] = 0

		fleet1.save()
		fleet2.insert()

		self.remove()

	def simulate(self):
		pass

	def turns(self, turns=0):
		return turns+1

	def resources(self):
		return []

	def fn_call(self, value=None):
		if value == None:
			return [0, self.call]
		else:
			self.call = value[1]

	def fn_ships(self, value=None):
		max = self.object.ships
		if value == None:
			returns = []
			for type, number in max.items():
				returns.append((type, Fleet.ship_types[type], number))
			print returns, self.ships.items()
			return returns, self.ships.items()
		else:
			ships = {}
			try:
				for type, number in value[1]:
					if not type in Fleet.ship_types.keys():
						raise ValueError("Invalid type selected")
					if number > max[type]:
						raise ValueError("Number to big")
					ships[type] = number
			except ValueError:
				pass

			self.ships = ships
