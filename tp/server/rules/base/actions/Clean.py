#!/usr/bin/env python

"""
This action removes objects which are ghosts.
"""

from tp.server.rules.base import UniverseAction

class CleanAction( UniverseAction ):
	def clean( self, obj ):
		if obj.ghost():
			# FIXME: If this object has children they will be no longer reachable...
			print "Removing %s because it's a ghost." % obj.id
			obj.remove()

	def __call__( self, top ):
		"""
		Walks around the universe cleaning up ghost objects.
		"""
		super( CleanAction, self )( top, "after", self.clean )

__all__ = [ 'CleanAction' ]
