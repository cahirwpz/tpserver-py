
import copy

from sbases.Object import Object, ObjectTypes
from sbases.Order import Order
from sbases.Message import Message

from sobjects import Fleet

class SplitFleet(Order):

	def do(self):
		# We need the original fleet
		fleet1 = Object(self.oid)
		
		# Create the new fleet
		fleet2 = copy.deepcopy(fleet1)
		fleet2.name = self.name

		# Add the ships to the new fleet
		for type, number in self.ships:
			fleet1.ships[type] -= number
			fleet2.ships[type] = number

		self.remove()

	def turns(self, turns=0):
		return turns+1

	def resources(self):
		return []

	def fn_name_(self, value=None):
		if value == None:
			return [0, self.name_]
		else:
			self.name_ = value[0]

	def fn_ships(self, value=None):
		max = self.object.ships
		if value == None:
			returns = []
			for type, number in max.items():
				returns.append((type, Fleet.ships[type], number))
			print returns, self.ships.items()
			return returns, self.ships.items()
		else:
			ships = {}

			try:
				for type, number in value[1]:
					if not type in Fleet.ships.keys():
						raise ValueError("Invalid type selected")
					if number > max[type]:
						raise ValueError("Number to big")
					ships[type] = number
			except:
				pass

			self.ships = ships

Order.types[3] = SplitFleet
