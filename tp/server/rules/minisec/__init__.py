
from tp.server.utils import ReparentOne
from tp.server.db import dbconn

from tp.server.bases.Board import Board
from tp.server.bases.Message import Message
from tp.server.bases.Object import Object

import random

from tp.server.bases.Ruleset import Ruleset as RulesetBase

# Generic Actions
import tp.server.rules.base.orders.NOp as NOp
import tp.server.rules.base.orders.MergeFleet as MergeFleet
import tp.server.rules.base.orders.Colonise as Colonise
import tp.server.rules.base.actions.Move as MoveAction
import tp.server.rules.base.actions.Clean as Clean
import tp.server.rules.base.actions.Win as Win

# Minisec specific imports
import orders.Move as Move
import orders.BuildFleet as BuildFleet
import orders.SplitFleet as SplitFleet
import actions.FleetCombat as FleetCombat
import actions.Heal as Heal

SIZE = 10000000
class Ruleset(RulesetBase):
	"""
	Minisec Ruleset...
	"""

	# The order orders and actions occur
	orderOfOrders = [
			BuildFleet, 		# Build all ships
			MergeFleet, 		# Merge fleets together
			SplitFleet, 		# Split any fleets - this means you can merge then split in one turn
			Clean, 				# Clean up fleets which no longer exist
			(Move, 'prepare'),  # Set the velocity of objects
			MoveAction, 		# Move all the objects about
			(Move, 'finalise'), # Check for objects which may have overshot the destination
			FleetCombat, 		# Perform a combat, ships may have escaped by moving away
			Colonise, 			# Colonise any planets, ships may have been destoryed or reached their destination
			Clean, 				# Remove all empty fleets
			Heal, 				# Repair any ships orbiting a friendly planet
			Win, 				# Figure out if there is any winner
			NOp, 				# NOp needs to occur last
	]

	def initalise(self):
		"""\
		Minisec 
		"""
		dbconn.use(self.game)

		# Need to create the top level universe object...

	def populate(self):		
		dbconn.use(game)
		
		# FIXME: Assuming that the Universe and the Galaxy exist.

		# Create this many systems
		for i in range(0, random.randint(int(max/2),max)):
			pos = random.randint(SIZE*-1, SIZE)*1000, random.randint(SIZE*-1, SIZE)*1000, random.randint(SIZE*-1, SIZE)*1000
			
			# Add system
			system = Object(type='tp.server.rules.base.objects.System')
			system.name = "System %s" % i
			system.size = random.randint(800000, 2000000)
			system.posx = pos[0]
			system.posy = pos[1]
			system.insert()
			ReparentOne(system)
			system.save()
			print "Created system (%s) with the id: %i" % (system.name, system.id)
			
			# In each system create a number of planets
			for j in range(0, random.randint(min, max)):
				planet = Object(type='tp.server.rules.base.objects.Planet')
				planet.name = "Planet %i" % (i*max + j)
				planet.size = random.randint(1000, 10000)
				planet.parent = system.id
				planet.posx = pos[0]+random.randint(1,100)*1000
				planet.posy = pos[1]+random.randint(1,100)*1000
				planet.insert()
				print "Created planet (%s) with the id: %i" % (planet.name, planet.id)


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

