
import math
from config import netlib

from tp.server.bases.Order import Order
from tp.server.bases.Object import Object
from tp.server.bases.Message import Message

from tp.server.utils import ReparentOne

def away(x):
	if x < 0:
		return int(-math.ceil(-x))
	else: 
		return int(math.ceil(x))

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

		# Work out what the maximum speed of this object is
		speed = obj.speed()

		xd, yd, zd = self.pos[0] - obj.posx, self.pos[1] - obj.posy, self.pos[2] - obj.posz

		# Make sure that we haven't missed the object
		if (obj.velx, obj.vely, obj.velz) != (0,0,0):
			if xd*obj.velx < 0 or yd*obj.vely < 0 or zd*obj.velz < 0:
				print "Object %i has overshot destination %s to (%i, %i, %i)" % \
					(obj.id, self.pos[0], obj.velx, obj.vely, obj.velz)
				obj.posx, obj.posy, obj.posz = self.pos
				ReparentOne(obj)
				obj.save()

		# Have we reached our destination?
		if self.pos == (obj.posx, obj.posy, obj.posz):
			print "Object %i has arrived at destination (%i, %i, %i)" % \
					(obj.id, obj.velx, obj.vely, obj.velz)
			obj.velx = obj.vely = obj.velz = 0
			obj.save()
			
			self.remove()

			# Send a message to the owner that the object has arrived...
			message = Message()
			message.bid = obj.owner
			message.slot = -1
			message.subject = "%s arrived" % obj.name
			message.body = """%s has arrive at it's destination (%i, %i, %i).""" % \
								(obj.name, obj.posx, obj.posy, obj.posz)
			message.insert()
			return

		# Are we moving at the right speed?
		if abs(obj.velx**2 + obj.vely**2 + obj.velx**2 - speed**2) > (0.01*speed)**2:
			distance = math.sqrt(xd**2 + yd**2 + zd**2)
			
			# Set the velocity so we are moving towards self.pos at speed
			obj.velx = away(min(speed * xd/distance, xd))
			obj.vely = away(min(speed * yd/distance, yd))
			obj.velz = away(min(speed * zd/distance, zd))
		
			print "Setting velocity of object %i to %r currently at %r destination %r" % (obj.id, 
				(obj.velx, obj.vely, obj.velz),
				(obj.posx, obj.posy, obj.posz),
				self.pos)
			obj.save()


	def turns(self, turns=0):
		obj = Object(self.oid)
		xd, yd, zd = self.pos[0] - obj.posx, self.pos[1] - obj.posy, self.pos[2] - obj.posz
		distance = math.sqrt(xd**2 + yd**2 + zd**2)
		
		return away(distance/obj.speed()) + turns

	def resources(self):
		return []

Move.typeno = 1
Order.types[Move.typeno] = Move
