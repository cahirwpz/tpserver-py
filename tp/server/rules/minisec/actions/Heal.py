"""\
Heals a fleet to full health if they are orbiting a friendly planet.
"""

from turn import WalkUniverse

from sbases.Object import Object

def do(top):
	def h(obj):
		if obj.type == "sobjects.Fleet":
			parent = Object(obj.parent)
			if parent.type == "sobjects.Planet":
				if obj.owner == parent.owner:
					print "Healing %s because orbiting %s" % (obj.name, parent.name)
					obj.damage = {}
					obj.save()
		
	WalkUniverse(top, "before", h)

