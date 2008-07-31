"""\
Adds the necesary resources to each planet
"""

from tp.server.bases.Object import Object
from tp.server.utils import WalkUniverse
from tp.server.bases.Resource import Resource
from tp.server.rules.dronesec.research.ResearchCalculator import ResearchCalculator as RC


def do(top):
	def h(obj):
		if obj.type.endswith("Planet"):
			if obj.owner != -1:
				resources, resourceRatio, researchRatio = RC.Economy(obj.owner)
				resources += 100

				resources = resources * resourceRatio
				obj.resources_add(Resource.byname('Credit'), resources)
				if obj.resources[Resource.byname('Credit')][0] > 100000:
					obj.resources[Resource.byname('Credit')][0] = 100000
				print "%s is  producing %s Credits" % (obj.name, resources)

				obj.damage = {}
				obj.save()
	WalkUniverse(top, "before", h)
