#!/usr/bin/env

from tp.server.model.Object import Object
from tp.server.model.Order import Order

def OrderGet():
	d = {}

	for id in Order.active():
		order = Order(id=id)
		if not d.has_key(order.type):
			d[order.type] = []

		d[order.type].append(order)
	return d

def ReparentOne(obj):
	# Reparent the object
	parents = Object.bypos([obj.posx, obj.posy, obj.posz], size=0, orderby=Object.bypos_size)
	print "Possible parents", parents
	
	obj.parent = 0
	parents = [id for (id, time) in parents if Object(id).type != obj.type]
	if parents:
		obj.parent = parents[0]
	else:
		print "No parents left! Using Universe."

__all__ = [ 'OrderGet', 'ReparentOne' ]
