
import math
from config import netlib

from turn import ReparentOne

from sbases.Order import Order
from sbases.Object import Object
from sbases.Message import Message

class Move(Order):
	"""\
Move to a point in space.
"""

	attributes = {\
		'pos': Order.Attribute("pos", (0,0,0), 'public', type=netlib.objects.constants.ARG_ABS_COORD, 
				desc="Where to go.")
	}
	
	def do(self):
		# We are going to have to modify the object so lets load it
		obj = Object(self.oid)

		if not hasattr(obj, "owner"):
			# Ekk we can't build an object if we don't have an owner...
			print "Could not do a move order because it was on an unownable object."
			self.remove()
		
		# Is this the first time we are moving?
		if (obj.velx, obj.vely, obj.velz) == (0,0,0):
			# Set the velocity
			obj.velx = math.ceil((self.pos[0] - obj.posx) / 2)
			obj.vely = math.ceil((self.pos[1] - obj.posy) / 2)
			obj.velz = math.ceil((self.pos[2] - obj.posz) / 2)

		if obj.velx != 0 or obj.vely != 0 or obj.velz != 0:
			# Move the object
			obj.posx, obj.posy, obj.posz = obj.posx + obj.velx, obj.posy + obj.vely, obj.posz + obj.velz

			# Just to make sure we don't get a division by zero error
			def div(a, b):
				try:
					return a/b
				except ZeroDivisionError:
					return 0

			# Make sure that we haven't missed the object
			if div(self.pos[0] - obj.posx, obj.velx) < 0 or \
				div(self.pos[1] - obj.posy, obj.vely) < 0 or \
				div(self.pos[2] - obj.posz, obj.velz) < 0:
				obj.posx, obj.posy, obj.posz = self.pos
		
		# Reparent the object
		ReparentOne(obj)
		print "New object parent is", obj.parent

		pos = obj.posx, obj.posy, obj.posz
		if self.pos == pos:
			obj.velx = obj.vely = obj.velz = 0
			self.remove()

			# Send a message to the owner that the object has arrived...
			message = Message()
			message.bid = obj.owner
			message.slot = -1
			message.subject = "%s arrived" % obj.name
			message.body = """%s has arrive at it's destination.""" % obj.name
			message.insert()

		obj.save()

	def turns(self, turns=0):
		return 2 + turns

	def resources(self):
		return []

Move.typeno = 1
Order.types[Move.typeno] = Move
