
from sbases.Object import Object

class Fleet(Object):

	def get_ships(self):
		return self._ships.items()
	ships = property(get_ships)

	def get_damage(self):
		totaldamage = 0

		for type, damage in self._damage:
			totaldamage += damage
			
		return totaldamage
	damage = property(get_damage)

Object.types[4] = Fleet
