
from tp.server.utils import ReparentOne
from tp.server.db import dbconn, convert

from tp.server.bases.Board    import Board
from tp.server.bases.Message  import Message
from tp.server.bases.Object   import Object

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
import orders.ProduceDrones as ProduceDrones
import orders.SplitFleet as SplitFleet
import actions.FleetCombat as FleetCombat
import actions.Heal as Heal
import actions.Turn as Turn

import random

from tp.server.utils.planetGenerator import PlanetGenerator


SIZE = 10000000
class Ruleset(RulesetBase):
	"""
	Dronesec Ruleset...
	"""
	name = "Dronesec"
	version = "0.0.1"

# Overlord orderss
# Moves
# Build Unit
# Research
# Combat
# Cap planet

	seed = 0
	# The order orders and actions occur
	orderOfOrders = [
			ProduceDrones, 		# Produce all Drones
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
			Turn, 				# Increase the Universe's "Turn" value
	]

	def initialise(self):
		"""\
		Dronesec
		"""
		dbconn.use(self.game)

		trans = dbconn.begin()
		try:
			RulesetBase.initialise(self)

			# Need to create the top level universe object...
			universe = Object(type='tp.server.rules.base.objects.Universe')
			universe.id     = 0
			universe.name   = "The Universe"
			universe.size   = SIZE
			universe.parent = 0
			universe.posx   = 0
			universe.posy   = 0
			universe.turn   = 0
			universe.insert()

			trans.commit()
		except:
			trans.rollback()
			raise

	def populate(self, maptype, numPlanets, numPlayers, maplayout, seed=None):
		"""\
		--populate <game> <Map Type> <number of Planets> <maximunum number of players> <Layout> <seed>
		    Maptypes so far can be normal, epic, and tug.
		    Number of Planets includes player planets
		    Layouts are currently a blank option. It could be used to determine randomness of map or a special layout to follow.
		    seed can be set for purposes of saved games. But fully random seeds are also allowed.

		"""

		dbconn.use(self.game)

		trans = dbconn.begin()

		try:
			# FIXME: Assuming that the Universe exists
			r = random.Random()
			r.seed(int(seed))
			self.seed = seed
			PG = PlanetGenerator(theSeed = int(self.seed))

			# In each system create a number of planets
			for j in range(0, int(numPlanets)):
				pos = r.randint(SIZE*-1, SIZE)*1000, r.randint(SIZE*-1, SIZE)*1000, r.randint(SIZE*-1, SIZE)*1000
				planet = Object(type='tp.server.rules.dronesec.objects.Planet')
				planet.name = "%s" % PG.genName()
				planet.size = r.randint(1000, 10000)
				planet.parent = 0
				planet.posx = pos[0]+r.randint(1,100)*1000
				planet.posy = pos[1]+r.randint(1,100)*1000
				planet.insert()
				print "Created planet (%s) with the id: %i" % (planet.name, planet.id)

			trans.commit()
		except:
			trans.rollback()
			raise

	def player(self, username, password, email='Unknown', comment='A Dronesec Player'):
		"""\
		Create a Solar System, Planet, and initial Fleet for the player, positioned randomly within the Universe.
		"""
		dbconn.use(self.game)

		trans = dbconn.begin()
		try:
			user = RulesetBase.player(self, username, password, email, comment)

      #First player created will always start at the same position should game be replayed
			r = random.Random()
			r.seed(self.seed)

			pos = r.randint(SIZE*-1, SIZE)*1000, r.randint(SIZE*-1, SIZE)*1000, r.randint(SIZE*-1, SIZE)*1000

#### Might have planets be created before hand and players join an already existing planet

			planet = Object(type='tp.server.rules.base.objects.Planet')
			planet.name = "%s Planet" % username
			planet.parent = 0
			planet.size = 100
			planet.posx = pos[0]
			planet.posy = pos[1]
			planet.owner = user.id
			planet.save()

			fleet = Object(type='tp.server.rules.dronesec.objects.Drones')
			fleet.parent = planet.id
			fleet.size = 3
			fleet.name = "%s First Fleet" % username
			fleet.ships = {1:3}
			(fleet.posx, fleet.posy, fleet.posz) = (planet.posx, planet.posy, planet.posz)
			fleet.owner = user.id
			fleet.save()

################

			trans.commit()

			return (user, planet, fleet)
		except:
			trans.rollback()
			raise

