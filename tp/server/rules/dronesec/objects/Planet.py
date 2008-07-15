import random

from tp.server.bases.Object import Object
from tp.server.bases.Combattant import Combattant

ACCESSABLE   = 0
MINABLE      = 1
INACCESSABLE = 2
class Planet(Object):
	attributes = { \
		'owner':     Object.Attribute('owner', -1, 'public'),
		'resources': Object.Attribute('resources', {}, 'protected'),
		'playerhome': Object.Attribute('playerhome', False, 'private')
		}
	orderclasses = (
		'tp.server.rules.dronesec.orders.ProduceDrones',
		'tp.server.rules.dronesec.orders.Research',
		)

	def ghost(self):
		"""\
		Planets never die - even when owned by the universe.
		"""
		return False

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
			raise TypeError("Resources somehow became negative!")

Planet.typeno = 3
Object.types[Planet.typeno] = Planet
