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


	seed = None
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
			MasterList.loadEconomyType()
			MasterList.loadCombatType()
			trans.commit()
		except:
			trans.rollback()
			raise

	def populate(self,  numPlanets , numPlayers = 2, maptype = 'random', seed=None, loadfile = None,):
		"""\
		--populate <game>  <number of Planets> <maximunum number of players> <Map Type> <seed> <load file>
		    Maptypes so far can be standard and random
		    Number of Planets includes player planets
		    
		    seed can be set for purposes of saved games. But fully random seeds are also allowed by typing in None
		    a loadfile does not need to be specified unless it is a loaded map.
		"""


		numPlanets = int(numPlanets)
		numPlayers = int(numPlayers)

		if numPlanets < numPlayers:
			print "Invalid: Number of Players cannot be more than then number of total planets"
			return

		dbconn.use(self.game)

		trans = dbconn.begin()

		try:
			
			# FIXME: Assuming that the Universe exists
			r = random.Random()

			if seed == 'None':
				seed = None

			if seed != None:
				self.seed = int(seed)
				r.seed(seed)

			PG = PlanetGenerator(theSeed = self.seed)
			

			if maptype == 'standard':
				if numPlayers < 2:
					print "Not enough players for a game"
					return

				import math
				size = SIZE * numPlanets * numPlayers
				divisions = (2.0 * math.pi)/numPlayers
				planetsPerDivision = int(math.floor(numPlanets / numPlayers))
				remainderPlanets = numPlanets % numPlayers
				
				
				locs = []
				
				locs.append((divisions, size * .75))
				#preset planet locations
				for plan in range(planetsPerDivision - 1):
					div = r.random() * divisions
					dist = r.random() * size
					locs.append((div, dist))

				for num in range(numPlayers):
					for x in range(planetsPerDivision):
						n = PG.genName()
						
						div = locs[x][0]
						dist = locs[x][1]

						posx = int(math.cos((divisions * num) + div) * dist)
						posy = int(math.sin((divisions * num) + div) * dist)
						posz = 0
						home = False
						if x == 0:
							home = True
						
						self.addPlanet(r, n, posx, posy, posz , -1, home)

				if remainderPlanets == 1:
					div = 0
					dist = 0
				elif remainderPlanets != 0:
				#Remainder Planets
					divisions = math.pi / remainderPlanets
					div = r.random() * div
					dist =r.randint(0, size)
				for num in range(remainderPlanets):
					n = PG.genName()

					posx = int(math.cos((divisions * num) + div) * dist)
					posy = int(math.sin((divisions * num) + div) * dist)
					posz = 0

					self.addPlanet(r, n, posx, posy, poz)

			elif maptype == 'load':
				if loadfile == None:
					print "Cannot populate game as no file was given"
					return
				import csv
				import os
				reader = csv.reader(open(os.path.join(os.path.abspath("./tp/server/rules/dronesec/maps/"),loadfile)))
				for name, x, y, z, size, home in reader:
					if name != 'Name':
						self.addPlanet(r, name, int(x), int(y), int(z), int(size), bool(home))

			else: #maptype =='random': 
				# In each system create a number of planets
				for j in range(0, int(numPlanets)):
					n = PG.genName()
					pos = r.randint(SIZE*-1, SIZE), r.randint(SIZE*-1, SIZE), r.randint(SIZE*-1, SIZE)
	
					self.addPlanet(r, n, pos[0], pos[1], pos[2] , -1, True)


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

			homeplanets = Object.bytype('tp.server.rules.dronesec.objects.Planet')
			homeplanets = [id for (id, time) in homeplanets if Object(id).playerhome and Object(id).owner == -1]
			
			if len(homeplanets) == 0:
				print "Sorry but the maximum amount of players for this map has been reached"
				return


			user = RulesetBase.player(self, username, password, email, comment)

			#First player created will always start at the same position should game be replayed
			r = random.Random()
			r.seed(self.seed + user.id)
			#### Might have planets be created before hand and players join an already existing planet
			homeplanets = Object.bytype('tp.server.rules.dronesec.objects.Planet')
			homeplanets = [id for (id, time) in homeplanets if Object(id).playerhome and Object(id).owner == -1]
			

			planet = Object(homeplanets[r.randint(0, len(homeplanets)-1)])

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

			print "%s has been assigned Planet: %s" % (username, planet.name)

			trans.commit()

			return (user, planet, overlord)
		except:
			trans.rollback()
			raise


	def addPlanet(self, r, name, x, y, z , size =-1 ,home = False):

		system = Object(type='tp.server.rules.base.objects.System')
		system.name = "System %s" % name
		system.size = r.randint(80, 200)
		system.posx = x
		system.posy = y
		system.posz = z
		system.insert()
		ReparentOne(system)
		system.save()

		planet = Object(type='tp.server.rules.dronesec.objects.Planet')
		planet.name = "%s" % name
		if size <= 0:
			size = r.randint(10, 100)
		planet.size = size
		planet.parent = system.id
		planet.posx = x+r.randint(1,10)
		planet.posy = y+r.randint(1,10)
		planet.posz = z + r.randint(1,10)
		planet.playerhome = home
		planet.insert()
		print "Created planet (%s) with the id: %i" % (planet.name, planet.id)
