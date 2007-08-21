
import random

from tp.server.rules.base.objects.Planet import Planet as PlanetBase

class Planet(PlanetBase):
	def factories(self):
		# Figure out the number of factories on this planet from the resource list.
		pass
	factories = property(factories)

