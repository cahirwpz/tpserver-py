from tp.server.bases.Object import Object

def ReparentOne(obj):
	# Reparent the object
	parents = Object.bypos([obj.posx, obj.posy, obj.posz], size=0, orderby=Object.bypos_size)
	print "Possible parents", parents

	obj.parent = 0
	parents = [id for (id, time) in parents if Object(id).type != obj.type
		and not Object(id).type.endswith("Fleet")]
	if parents:
		obj.parent = parents[0]
	else:
		print "No parents left! Using Universe."
