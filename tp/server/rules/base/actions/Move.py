#!/usr/bin/env python

from tp.server.rules.base import UniverseAction
from tp.server.rules.base.utils import ReparentOne

class MoveAction( UniverseAction ):
	"""
	Moves any object which has a velocity.
	"""

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
		super( MoveAction, self )( top, "after", self.move )

__all__ = [ 'MoveAction' ]
