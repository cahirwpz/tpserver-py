
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
				if type in self.ships.keys():
					for d in damage:
						totaldamage += damage
			
			return totaldamage
	
	ship_types = {0: "Scout", 1:"Frigate", 2:"Battleship"}
	ship_hp = {0: 2, 1:4, 2:6}
	ship_damage = {0:(0, 0), 1:(0, 2), 2:(1,3)}

	def damage_do(self, amount):
		"""\
		Damages a fleet. Can be called with either a single
		integer or a tuple of integers.
		"""
		if type(amount) == TupleType:
			for a in amount:
				self.do_damage(a)
			return

		# Run a consistancy check
		# Check the ships actually exist
		for type, number in self.ships:
			if number < 1:
				del self.ships[type]

		# Check the damage goes to the right place
		for type, damage in self.damage:
			if not type in self.ships.keys():
				del self.damage[type]

		# Find the largest ship type.
		s = self.ships.keys()
		s.sort()
		s.reverse()
		type = s[0]
		damage = self.damage[type]

		# Condense the damage
		if len(damage)+1 > self.ships[type]:
			damage.sort()
			if damage[0] + amount > self.ship_hp[type]:
				damage[-1] += amount
			else:
				damage[0] += amount
		else:
			damage.append(amount)
		
		if damage[-1] > self.ship_hp[type]:
			self.ships[type] -= 1
			if self.ships[type] < 1:
				del self.ships[type]
			del damage[-1]

	def damage_get(self, fail=True):
		"""\
		Returns the amount of damage this fleet can do.
		"""
		r = []
		for type, no in self.ships:
			r.extend([self.ship_damage[type][fail]] * no)
		return r

	

Fleet.typeno = 4
Object.types[Fleet.typeno] = Fleet
