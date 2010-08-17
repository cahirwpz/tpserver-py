#!/usr/bin/env python

from tp.server.rules.base import UniverseAction

class HealAction( UniverseAction ):
	"""
	Heals a fleet to full health if they are orbiting a friendly planet.
	"""

	def heal( self, obj ):
		if obj.type == "sobjects.Fleet":
			parent = Object(obj.parent)
			if parent.type == "sobjects.Planet":
				if obj.owner == parent.owner:
					print "Healing %s (%s) because orbiting %s (%s)" % (obj.name, obj.id, parent.name, parent.id)
					obj.damage = {}
					obj.save()
			
	def __call__( self, top ):
		super( HealAction, self)( top, "before", self.heal )

__all__ = [ 'HealAction' ]
