#!/usr/bin/env python

"""
Moves any object which has a velocity.
"""

from tp.server.utils import WalkUniverse, ReparentOne
from tp.server.rules.base import Action

class MoveAction( Action ):
	def move( self, obj ):
		if (obj.velx, obj.vely, obj.velz) != (0,0,0):
			print "Moving object %s from (%s, %s, %s) to (%s, %s, %s)" % (
				obj.id, 
				obj.posx, obj.posy, obj.posz, 
				obj.posx + obj.velx, obj.posy + obj.vely, obj.posz + obj.velz)
			
			obj.posx, obj.posy, obj.posz = obj.posx + obj.velx, obj.posy + obj.vely, obj.posz + obj.velz
			# FIXME: This could be dangerous
			ReparentOne(obj)
			obj.save()
			
	def __call__( self, top ):
		WalkUniverse( top, "after", self.move )

__all__ = [ 'MoveAction' ]
