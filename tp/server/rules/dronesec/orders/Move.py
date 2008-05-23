
import math
from tp import netlib

from tp.server.bases.Order import Order
from tp.server.bases.Object import Object
from tp.server.bases.Message import Message

from tp.server.utils import ReparentOne

def away(x):
	if x < 0:
		return int(-math.ceil(-x))
	else: 
		return int(math.ceil(x))

def closest(*args):
	x = args[0]
	for y in args[1:]:
		if min(abs(y), abs(x)) == abs(y):
			x = y
	return x

class Move(Order):
	"""\
Move to a point in space.
"""
	typeno = 1

	attributes = {\
		'pos': Order.Attribute("pos", (0,0,0), 'public', type=netlib.objects.constants.ARG_ABS_COORD, 
				desc="Where to go.")
	}
	
	def do(self, action):
		# We are going to have to modify the object so lets load it
		obj = Object(self.oid)

		# Work out what the maximum speed of this object is
		speed = obj.speed()

		xd, yd, zd = self.pos[0] - obj.posx, self.pos[1] - obj.posy, self.pos[2] - obj.posz

		if action == 'finalise':
			# Make sure that we haven't missed the object
			if (obj.velx, obj.vely, obj.velz) != (0,0,0):
				if xd*obj.velx < 0 or yd*obj.vely < 0 or zd*obj.velz < 0:
					print "Object %i (%s) has overshot destination %s to (%i, %i, %i)" % \
						(obj.id, obj.name, self.pos, obj.velx, obj.vely, obj.velz)
					obj.posx, obj.posy, obj.posz = self.pos
					ReparentOne(obj)
					obj.save()
	
			# Have we reached our destination?
			if self.pos == (obj.posx, obj.posy, obj.posz):
				print "Object %i (%s) has arrived at destination (%i, %i, %i)" % \
						(obj.id, obj.name, obj.posx, obj.posy, obj.posz)
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
		
		elif action == 'prepare':
			distance = math.sqrt(xd**2 + yd**2 + zd**2)
			
			if distance == 0:
				return
	
			# Set the velocity so we are moving towards self.pos at speed
			velx = away(closest(speed * xd/distance, xd))
			vely = away(closest(speed * yd/distance, yd))
			velz = away(closest(speed * zd/distance, zd))
			
			if (velx, vely, velz) != (obj.velx, obj.vely, obj.velz):
				print "Setting velocity of object %i to %r currently at %r destination %r" % (obj.id, 
					(velx, vely, velz),
					(obj.posx, obj.posy, obj.posz),
					self.pos)
				obj.velx, obj.vely, obj.velz = velx, vely, velz
				obj.save()
			return
		else:
			raise Exception("Unknown action!")

	def turns(self, turns=0):
		obj = Object(self.oid)
		xd, yd, zd = self.pos[0] - obj.posx, self.pos[1] - obj.posy, self.pos[2] - obj.posz
		distance = math.sqrt(xd**2 + yd**2 + zd**2)
		
		return away(distance/obj.speed()) + turns

	def resources(self):
		return []
