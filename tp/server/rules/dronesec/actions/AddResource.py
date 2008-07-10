"""\
Adds the necesary resources to each planet
"""

from tp.server.bases.Object import Object
from tp.server.utils import WalkUniverse
from tp.server.bases.Resource import Resource
from tp.server.rules.dronesec.objects.Planet import Planet
from tp.server.rules.dronesec.bases.Research import Research
from tp.server.rules.dronesec.bases.Player import Player



def do(top):
	def h(obj):
		if obj.type.endswith("Planet"):
			if obj.owner != -1:
				resources = 100
				resourceRatio = 1
				researches = Research.bytype('tp.server.rules.dronesec.research.EconomyType')
				res = []
				for x in Player(obj.owner).research:
					if x in researches:
						res.append(x)
				researches = res
				if researches:
					for id in researches:
						resources += Research(id).resources
						resourceRatio += Research(id).resourcesRatio
				resources = resources * resourceRatio
				obj.resources_add(Resource.byname('Credit'), resources)
				print "%s is  producing %s Credits" % (obj.name, resources)

				obj.damage = {}
				obj.save()
	WalkUniverse(top, "before", h)
