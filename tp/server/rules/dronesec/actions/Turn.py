"""\
Updates the Turn number for the Universe.
"""

from tp.server.bases.Object import Object

def do(top):
	"""
	Action Method for Turn
	
	Universe's Turn is incremented.
	"""
	universe = Object(id=0)
	universe.turn += 1
	print "Turn number is now", universe.turn
	universe.save()

