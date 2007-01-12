
import tp.server.rules.base as base

from tp.server.utils import ReparentOne
from tp.server.bases.Board import Board
from tp.server.bases.Message import Message
from tp.server.bases.Object import Object

import random

SIZE = 10000000

def spawn_player(player):
	"""\
	Create a Solar System, Planet, and initial Fleet for the player, positioned randomly within the Universe.
	"""

	player_name = player.username

	board = Board()
	board.id = player.id
	board.name = "Private message board for %s" % player_name
	board.desc = """\
This board is used so that stuff you own (such as fleets and planets) \
can inform you of what is happening in the universe. \
"""
	board.save()

	# Add the first message
	message = Message()
	message.bid = board.id
	message.slot = -1
	message.subject = "Welcome to the Universe!"
	message.body = """\
Welcome, %s, to the python Thousand Parsec server. Hope you have fun! \
""" % (player_name)
	message.save()


	pos = random.randint(SIZE*-1, SIZE)*1000, random.randint(SIZE*-1, SIZE)*1000, random.randint(SIZE*-1, SIZE)*1000

	system = Object(type='tp.server.rules.base.objects.System')
	system.name = "%s Solar System" % player_name
	system.parent = 0
	system.size = random.randint(800000, 2000000)
	(system.posx, system.posy, junk) = pos
	ReparentOne(system)
	system.owner = player.id
	system.save()

	planet = Object(type='tp.server.rules.base.objects.Planet')
	planet.name = "%s Planet" % player_name
	planet.parent = system.id
	planet.size = 100
	planet.posx = system.posx+random.randint(1,100)*1000
	planet.posy = system.posy+random.randint(1,100)*1000
	planet.owner = player.id
	planet.save()

	fleet = Object(type='tp.server.rules.minisec.objects.Fleet')
	fleet.parent = planet.id
	fleet.size = 3
	fleet.name = "%s First Fleet" % player_name
	fleet.ships = {1:3}
	(fleet.posx, fleet.posy, fleet.posz) = (planet.posx, planet.posy, planet.posz)
	fleet.owner = player.id
	fleet.save()

	return True

