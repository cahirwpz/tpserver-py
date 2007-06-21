
import random

from tp.server.bases.Object import Object
from tp.server.bases.Combattant import Combattant

ACCESSABLE   = 0
MINABLE      = 1
INACCESSABLE = 2
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
		res = []
		for id, values in self.resources.items():
			res.append((id, values[0], values[1], values[2]))

		return res

	def resources_add(self, resource, amount, type=ACCESSABLE):
		if not self.resources.has_key(resource):
			self.resources[resource] = [0, 0, 0]
		self.resources[resource][type] += amount

		if self.resources[resource][type] < 0:
			raise TypeError("Resources some how became negative!")

Planet.typeno = 3
Object.types[Planet.typeno] = Planet
