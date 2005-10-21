"""\
This module impliments combat as found in the MiniSec document.
"""

import random

from turn import WalkUniverse

def do(top):
	"""
	Walks around the universe cleaning up ghost objects.
	"""
	def c(obj):
		if obj.ghost():
			# FIXME: If this object has children they will be no longer reachable...
			print "Removing %s because it's a ghost." % obj.id
			obj.remove()

	WalkUniverse(top, "after", c)
