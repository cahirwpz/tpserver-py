
from tp.server.bases.Object import Object

def WalkUniverse(top, order, callback, *args, **kw):
	"""\
	Walks around the universe and calls a command for each object.
	
	If the first argument is "before" parents will be called before there children.
	If the first argument is "after" parents will be called after there children.
	"""
	if order == "before":
		callback(top, *args, **kw)

	for id in top.contains():
		WalkUniverse(Object(id), order, callback, *args, **kw)

	if order == "after":
		callback(top, *args, **kw)

def OrderGet(top, d={}):
	"""
	Walks around the universe and puts the orders into the given dictionary.
	"""

	def o(obj, d=d):
		if obj.orders() > 0:
			# Find the first valid order on this object
			while True:
				order = Order(obj.id, 0)

				if False:
					order = None
				else:
					break

			if not d.has_key(order.type):
				d[order.type] = []

			d[order.type].append(order)

	WalkUniverse(top, "before", o)

def ReparentOne(obj):
	# Reparent the object
	parents = Object.bypos([obj.posx, obj.posy, obj.posz], size=0, orderby="size ASC")
	print "Possible parents", parents
	
	obj.parent = 0
	parents = [id for (id, time) in parents if Object(id).type != obj.type]
	if parents:
		obj.parent = parents[0]
	else:
		print "No parents left! Using Universe."
