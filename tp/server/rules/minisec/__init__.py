
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
	name = "Minisec"
	version = "0.0.1"

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



	def populate(self, seed, system_min, system_max, planet_min, planet_max):
		"""\
		--populate <game> <random seed> <min systems> <max systems> <min planets> <max planets>
		
			Populate a universe with a number of systems and planets.
			The number of systems in the universe is dictated by min/max systems.
			The number of planets per system is dictated by min/max planets.
		"""
		seed, system_min, system_max, planet_min, planet_max = (int(seed), int(system_min), int(system_max), int(planet_min), int(planet_max))

		dbconn.use(self.game)
		
		# FIXME: Assuming that the Universe and the Galaxy exist.
		random.seed(seed)

		# Create this many systems
		for i in range(0, random.randint(system_min, system_max)):
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
			for j in range(0, random.randint(planet_min, planet_max)):
				planet = Object(type='tp.server.rules.base.objects.Planet')
				planet.name = "Planet %i in %s" % (j, system.name)
				planet.size = random.randint(1000, 10000)
				planet.parent = system.id
				planet.posx = pos[0]+random.randint(1,100)*1000
				planet.posy = pos[1]+random.randint(1,100)*1000
				planet.insert()
				print "Created planet (%s) with the id: %i" % (planet.name, planet.id)

	def player(self, username, password, email='Unknown', comment='A Minisec Player'):
		"""\
		Create a Solar System, Planet, and initial Fleet for the player, positioned randomly within the Universe.
		"""
		dbconn.use(self.game)

		user = RulesetBase.player(self, username, password, email, comment)

		pos = random.randint(SIZE*-1, SIZE)*1000, random.randint(SIZE*-1, SIZE)*1000, random.randint(SIZE*-1, SIZE)*1000

		system = Object(type='tp.server.rules.base.objects.System')
		system.name = "%s Solar System" % username
		system.parent = 0
		system.size = random.randint(800000, 2000000)
		(system.posx, system.posy, junk) = pos
		ReparentOne(system)
		system.owner = user.id
		system.save()

		planet = Object(type='tp.server.rules.base.objects.Planet')
		planet.name = "%s Planet" % username
		planet.parent = system.id
		planet.size = 100
		planet.posx = system.posx+random.randint(1,100)*1000
		planet.posy = system.posy+random.randint(1,100)*1000
		planet.owner = user.id
		planet.save()

		fleet = Object(type='tp.server.rules.minisec.objects.Fleet')
		fleet.parent = planet.id
		fleet.size = 3
		fleet.name = "%s First Fleet" % username
		fleet.ships = {1:3}
		(fleet.posx, fleet.posy, fleet.posz) = (planet.posx, planet.posy, planet.posz)
		fleet.owner = user.id
		fleet.save()

