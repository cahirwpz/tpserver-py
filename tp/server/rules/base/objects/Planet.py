
from sbases.Object import Object
from sbases.Combattant import Combattant

class Planet(Object, Combattant):
	attributes = { \
		'owner': Object.Attribute('owner', -1, 'public'),
		'resources': Object.Attribute('resources', {}, 'public'),
	}
	orderclasses = ('sorders.NOp', 'sorders.BuildFleet', 'sorders.Mine')

	def ghost(self):
		"""\
		Planets never die - even when owned by the universe.
		"""
		return False

	#############################################
	# Combat functions
	#############################################

	damage = 0
	def dead(self):
		"""\
		Planets are dead went delt 12 damage.
		"""
		return self.damage > 12
	
	def damage_set(self, damage):
		if type(amount) in (TupleType, ListType):
			for a in amount:
				self.damage_do(a)
			return
		
		self.damage = self.damage + damage

	def damage_get(self, fail=False):
		return (6, 2)[fail]

	def resources_get(self):
		return []

Planet.typeno = 3
Object.types[Planet.typeno] = Planet
