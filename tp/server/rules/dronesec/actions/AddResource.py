"""\
Adds the necesary resources to each planet
"""

from tp.server.bases.Object import Object
from tp.server.utils import WalkUniverse
from tp.server.bases.Resource import Resource
from tp.server.rules.dronesec.objects.Planet import Planet
def do(top):
	def h(obj):
		if obj.type.endswith("Planet"):
			if obj.owner != -1:
					obj.resources_add(Resource.byname('Credit'), 100)
					print "%s is  producing 100 Credits" % (obj.name)
					obj.damage = {}
					obj.save()
	WalkUniverse(top, "before", h)
