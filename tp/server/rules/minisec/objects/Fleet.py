
from sbases.Object import Object

class Fleet(Object):
	type = 4

	def fn_ships(self, value=None):
		if value == None:
			return self.ships.items()

	def fn_damage(self, value=None):
		if value == None:
			totaldamage = 0

			for type, damage in self.damage:
				totaldamage += damage
			
			return totaldamage
	
	ships = {0: "Scout", 1:"Frigate", 2:"Battleship"}

Object.types[4] = Fleet
