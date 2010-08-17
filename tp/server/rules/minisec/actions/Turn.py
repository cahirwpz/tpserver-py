#!/usr/bin/env python

from tp.server.rules.base import Action

class TurnAction( Action ):
	"""
	Increases age of the universe.
	"""

	def __call__( self, top ):
		universe = Object(id=0)
		universe.turn += 1
		print "Turn number is now", universe.turn
		universe.save()

__all__ = [ 'TurnAction' ]
