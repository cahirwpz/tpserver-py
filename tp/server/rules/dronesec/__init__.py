from tp.server.utils import ReparentOne
from tp.server.db import dbconn, convert

from tp.server.bases.Board    import Board
from tp.server.bases.Message  import Message
from tp.server.bases.Object   import Object
from tp.server.bases.Resource import Resource
from tp.server.bases.Ruleset import Ruleset as RulesetBase

from bases.Player import Player
from bases.Drone import Drone
from bases.Research import Research


# Generic Actions
import tp.server.rules.base.orders.NOp as NOp

import tp.server.rules.base.actions.Clean as Clean
import tp.server.rules.base.actions.Win as Win

# Dronesec specific imports
import actions.Defeat as Defeat
import orders.Move as Move
import orders.ProduceDrones as ProduceDrones
import actions.Move as MoveAction
import actions.Heal as Heal
import actions.Turn as Turn
import actions.Capture as Capture
import actions.AddResource as AddResource
import actions.MoveDrones as MoveDrones
import actions.SetDestination as SetDestination
import actions.Automerge as Automerge
import actions.FleetCombat as FleetCombat
import orders.Repel as Repel
import orders.Attract as Attract
import orders.Stop as Stop
import orders.Research as ResearchOrder

import random

from tp.server.utils.planetGenerator import PlanetGenerator


SIZE = 1000
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
			Attract,			# Attract units
			Repel,				# Repel units
			Stop,				# Drones will stop moving
			ResearchOrder, 			# Implements Research Upgrades
			SetDestination,		# Sets target location
			MoveDrones, 		# Move Drones
			ProduceDrones, 		# Produce all Drones
			Automerge, 			# Merge Drones of the same type
			FleetCombat, 		# Combat
			(Move, 'prepare'),  # Set the velocity of objects
			MoveAction, 		# Move all the objects about
			(Move, 'finalise'), # Check for objects which may have overshot the destination
			Capture, 			# Captures Planets that can be captured
			AddResource,		# Add Resource to planet
			Clean, 				# Remove all empty fleets
			Heal, 				# Repair any ships orbiting a friendly planet
			Defeat, 			# Remove overlords if a player has no more units
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
			#initialize Credits resource
			r = Resource()
			r.namesingular = "Credit"
			r.nameplural   = "Credits"
			r.unitsingular = 'cr'
			r.unitplural = 'cr'
			r.desc = "Primary Resource of Drones"
			r.weight = 0
			r.size   = 10
			r.insert()
			from drones.Dronepedia import Dronepedia
			from research.MasterList import MasterList
			D = Dronepedia()
			MasterList.loadUnitType()
			MasterList.loadWorldType()
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
			if seed != None:
				self.seed = int(seed)
				r.seed(seed)

			PG = PlanetGenerator(theSeed = self.seed)
			# In each system create a number of planets
			for j in range(0, int(numPlanets)):
				n = PG.genName()
				pos = r.randint(SIZE*-1, SIZE), r.randint(SIZE*-1, SIZE), r.randint(SIZE*-1, SIZE)
				system = Object(type='tp.server.rules.base.objects.System')
				system.name = "System %s" % n
				system.size = r.randint(80, 200)
				system.posx = pos[0]
				system.posy = pos[1]
				system.insert()
				ReparentOne(system)
				system.save()

				planet = Object(type='tp.server.rules.dronesec.objects.Planet')
				planet.name = "%s" % n
				planet.size = r.randint(10, 100)
				planet.parent = system.id
				planet.posx = pos[0]+r.randint(1,10)
				planet.posy = pos[1]+r.randint(1,10)
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
			r.seed(self.seed + user.id)
			pos = r.randint(SIZE*-1, SIZE), r.randint(SIZE*-1, SIZE), r.randint(SIZE*-1, SIZE)
	#### Might have planets be created before hand and players join an already existing planet

			system = Object(type='tp.server.rules.base.objects.System')
			system.name = "%s Solar System" % username
			system.parent = 0
			system.size = r.randint(80, 200)
			(system.posx, system.posy, junk) = pos
			ReparentOne(system)
			system.save()


			planet = Object(type='tp.server.rules.dronesec.objects.Planet')
			planet.name = "%s Planet" % username
			planet.parent = system.id
			planet.size = 100
			planet.posx = pos[0]
			planet.posy = pos[1]
			planet.owner = user.id
			planet.resources_add(Resource.byname('Credit'), 100)
			planet.save()

			overlord = Object(type='tp.server.rules.dronesec.objects.overlord.Fleet')
			overlord.parent = planet.id
			overlord.size = 3
			overlord.name = "%s Overlord" % username
			overlord.ships = {0:1}
			(overlord.posx, overlord.posy, overlord.posz) = (planet.posx, planet.posy, planet.posz)
			overlord.owner = user.id
			overlord.save()

			players = Player()
			players.BuildList()
			players.insert()

			trans.commit()

			return (user,system, planet, overlord)
		except:
			trans.rollback()
			raise
