
from sbases.Object import Object

class Fleet(Object):
	attributes = { \
		'owner': Object.Attribute('owner', -1, 'public'),
		'ships': Object.Attribute('ships', {}, 'protected'),
		'damage': Object.Attribute('damage', {}, 'protected'),
	}
	orderclasses = ('sorders.NOp', 'sorders.Move', 'sorders.SplitFleet', 'sorders.MergeFleet',
					'sorders.Colonise',)

	def fn_ships(self, value=None):
		if value == None:
			return self.ships.items()

	def fn_damage(self, value=None):
		if value == None:
			totaldamage = 0

			for type, damage in self.damage:
				totaldamage += damage
			
			return totaldamage
	
	ship_types = {0: "Scout", 1:"Frigate", 2:"Battleship"}
	
Fleet.typeno = 4
Object.types[Fleet.typeno] = Fleet
