"""\
Heals a fleet to full health if they are orbiting a friendly planet.
"""

from tp.server.bases.Object import Object

def do(top):
	universe = Object(id=0)
	universe.turn += 1
	print "Turn number is now", universe.turn
	universe.save()

