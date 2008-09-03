"""\
Sets a Drones target location and current orders based on its parent overlord
"""
from tp.server.bases.Object import Object
from tp.server.utils import WalkUniverse
from tp.server.rules.dronesec.objects.overlord.Fleet import Fleet
from tp.server.rules.dronesec.objects.Fleet import Fleet as Drone

def getOverlords():
	"""
	Returns a list populated by the object instances of all overlords.
	"""
	overlords = Object.bytype('tp.server.rules.dronesec.objects.overlord.Fleet')
	list = []
	for overlord in overlords:
		o = Object(id = overlord[0])
		list.append(o)
	return list

def do(top):
	"""
	Action Method for SetDestination
	
	Drone Fleet's target and orders are assigned from their overlords last given commands.
	"""
	overlords = getOverlords()
	def h(obj):
		if isinstance(obj, Drone) and not hasattr(obj, "command"):
			for over in overlords:
				if over.owner == obj.owner:
					obj.target = over.pos
					obj.ordered = over.command
					obj.save()
	WalkUniverse(top, "before",h)
