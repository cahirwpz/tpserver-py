
from types import TupleType, ListType

from sbases.Object import Object
from sbases.Combattant import Combattant

class Fleet(Object, Combattant):
	attributes = { \
		'owner': Object.Attribute('owner', -1, 'public'),
		'ships': Object.Attribute('ships', {}, 'protected'),
		'damage': Object.Attribute('damage', {}, 'protected'),
	}
	orderclasses = ('sorders.NOp', 'sorders.Move', 'sorders.SplitFleet', 'sorders.MergeFleet',
					'sorders.Colonise',)

	ship_types = {0: "Scout", 1:"Frigate", 2:"Battleship"}
	ship_hp = {0: 2, 1:4, 2:6}
	ship_damage = {0:(0, 0), 1:(2, 0), 2:(3,1)}

	def fn_ships(self, value=None):
		if value == None:
			return self.ships.items()

	def fn_damage(self, value=None):
		if value == None:
			return sum(map(sum, self.damage.values()))

			totaldamage = 0
			for type, damage in self.damage:
				if type in self.ships.keys():
					for d in damage:
						totaldamage += damage
			
			return totaldamage
			
	def tidy(self):
		"""\
		Fix up the ships and damage stuff.
		"""
		# Run a consistancy check
		# Check the ships actually exist
		for t, number in self.ships.items():
			if number < 1:
				del self.ships[t]

		# Check the damage goes to the right place
		for t, damage in self.damage.items():
			if not t in self.ships.keys():
				del self.damage[t]

	def ghost(self):
		"""\
		Returns if the fleet has no ships.
		"""
		self.tidy()
		return len(self.ships.keys()) < 1

	#############################################
	# Combat functions
	#############################################

	def dead(self):
		"""\
		Checks if this object is a can still participate in combat.
		"""
		return self.ghost() or self.ships.keys() == [0,]
		
	def damage_do(self, amount):
		"""\
		Damages a fleet. Can be called with either a single
		integer or a tuple of integers.
		"""
		if type(amount) in (TupleType, ListType):
			for a in amount:
				self.damage_do(a)
			return

		self.tidy()

		# Find the largest ship type.
		s = self.ships.keys()
		s.sort()
		s.reverse()
		t = s[0]
	
		if not self.damage.has_key(t):
			self.damage[t] = []
		damage = self.damage[t]

		# Condense the damage
		if len(damage)+1 > self.ships[t]:
			damage.sort()
			if damage[0] + amount >= self.ship_hp[t]:
				damage[-1] += amount
			else:
				damage[0] += amount
		else:
			damage.append(amount)
		
		if damage[-1] >= self.ship_hp[t]:
			self.ships[t] -= 1
			if self.ships[t] < 1:
				del self.ships[t]
			del damage[-1]

	def damage_get(self, fail=False):
		"""\
		Returns the amount of damage this fleet can do.
		"""
		r = []
		for type, no in self.ships.items():
			r.extend([self.ship_damage[type][fail]] * no)
		return r

Fleet.typeno = 4
Object.types[Fleet.typeno] = Fleet
