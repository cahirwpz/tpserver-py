import math
from tp.server.bases.Object import Object
from tp.server.utils import WalkUniverse, ReparentOne
from tp.server.rules.dronesec.objects.Fleet import Fleet as Drone


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

def do(top):
	def move(obj):
		if isinstance(obj, Drone) and not hasattr(obj, "command"):
			if obj.ordered == 0:
				obj.velx, obj.vely, obj.velz = 0, 0, 0
			else:
				##Copy from Move.py
				speed = int(obj.speed())
				xd, yd, zd = obj.target[0] - obj.posx, obj.target[1] - obj.posy, obj.target[2] - obj.posz
				distance = math.sqrt(xd**2 + yd**2 + zd**2)

				if distance == 0:
					pass

				# Set the velocity so we are moving towards self.pos at speed
				velx = away(closest(speed * xd/distance, xd))
				vely = away(closest(speed * yd/distance, yd))
				velz = away(closest(speed * zd/distance, zd))

				if (velx, vely, velz) != (obj.velx, obj.vely, obj.velz):
					print "Setting velocity of object %i to %r currently at %r destination %r" % (obj.id,
						(velx, vely, velz),
						(obj.posx, obj.posy, obj.posz),
						obj.target)
					if obj.ordered == 1:
						obj.velx, obj.vely, obj.velz = velx, vely, velz
					elif obj.ordered == 2:
						obj.velx, obj.vely, obj.velz = -velx, -vely, -velz

				elif (obj.posx, obj.posy, obj.posz) != obj.target:
					print "Moving object %s from (%s, %s, %s) to (%s, %s, %s)" % (
						obj.id,
						obj.posx, obj.posy, obj.posz,
						obj.posx + obj.velx, obj.posy + obj.vely, obj.posz + obj.velz)

					obj.posx, obj.posy, obj.posz = obj.posx + obj.velx, obj.posy + obj.vely, obj.posz + obj.velz

					#Check to see if it overshot.
					if (obj.velx, obj.vely, obj.velz) != (0,0,0):
						if xd*obj.velx < 0 or yd*obj.vely < 0 or zd*obj.velz < 0:
							print "Object %i (%s) has overshot destination %s to (%i, %i, %i)" % \
								(obj.id, obj.name, self.pos, obj.velx, obj.vely, obj.velz)
							obj.posx, obj.posy, obj.posz = obj.target
							obj.velx, obj.vely, obj.velz = (0,0,0)

				# FIXME: This could be dangerous.
				ReparentOne(obj)
				obj.save()

	WalkUniverse(top, "after", move)