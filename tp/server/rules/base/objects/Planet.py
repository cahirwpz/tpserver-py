
import random

from tp.server.bases.Object import Object
from tp.server.bases.Combattant import Combattant

class Planet(Object, Combattant):
	attributes = { \
		'owner':     Object.Attribute('owner', -1, 'public'),
		'resources': Object.Attribute('resources', {}, 'protected'),
	}
	orderclasses = ('tp.server.rules.base.orders.NOp', 'tp.server.rules.minisec.orders.BuildFleet')

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
	
	def damage_do(self, damage):
		if type(amount) in (TupleType, ListType):
			for a in amount:
				self.damage_do(a)
			return
		
		self.damage = self.damage + damage

	def damage_get(self, fail=False):
		return (6, 2)[fail]

	def fn_resources(self, value=None):
		r = random.Random()
		r.seed(self.id)

		res = []
		ids = r.sample(range(0, 3), r.randint(0, 3))
		for id in ids:
			res.append((id, r.randint(0, 10), r.randint(0, 100), r.randint(0, 1000)))

		return res

Planet.typeno = 3
Object.types[Planet.typeno] = Planet
