"""\
Moves any object which has a velocity.
"""

from tp.server.utils import WalkUniverse, ReparentOne

def do(top):
	def move(obj):
		if (obj.velx, obj.vely, obj.velz) != (0,0,0):
			obj.posx, obj.posy, obj.posz = obj.posx + obj.velx, obj.posy + obj.vely, obj.posz + obj.velz
			# FIXME: This could be dangerous
			ReparentOne(obj)
			obj.save()
		
	WalkUniverse(top, "after", move)
