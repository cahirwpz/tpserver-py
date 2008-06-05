"""\
Heals a fleet to full health if they are orbiting a friendly planet.
"""

from tp.server.bases.Object import Object
from tp.server.utils import WalkUniverse

def do(top):
	def h(obj):
		if obj.type == "sobjects.Fleet":
			parent = Object(obj.parent)
			if parent.type == "sobjects.Planet":
				if obj.owner == parent.owner:
					print "Healing %s (%s) because orbiting %s (%s)" % (obj.name, obj.id, parent.name, parent.id)
					obj.damage = {}
					obj.save()
		
	WalkUniverse(top, "before", h)

