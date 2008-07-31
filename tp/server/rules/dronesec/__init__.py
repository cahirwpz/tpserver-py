from tp.server.utils import ReparentOne
from tp.server.db import dbconn, convert

from tp.server.bases.Board    import Board
from tp.server.bases.Message  import Message
from tp.server.bases.Object   import Object
from tp.server.bases.Resource import Resource
from tp.server.bases.Ruleset import Ruleset as RulesetBase
from tp.server.bases.Category import Category
from tp.server.bases.Design import Design
from tp.server.bases.Component import Component

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
import actions.SyncDB as SyncDB
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
	version = "0.0.2"

	seed = None
	# The order orders and actions occur
	orderOfOrders = [
			Attract,            # Attract units
			Repel,              # Repel units
			Stop,               # Drones will stop moving
			ResearchOrder,      # Implements Research Upgrades
			SetDestination,     # Sets target location
			MoveDrones,         # Move Drones
			ProduceDrones,      # Produce all Drones
			Automerge,          # Merge Drones of the same type
			FleetCombat,        # Combat
			(Move, 'prepare'),  # Set the velocity of objects
			MoveAction,         # Move all the objects about
			(Move, 'finalise'), # Check for objects which may have overshot the destination
			Capture,            # Captures Planets that can be captured
			AddResource,        # Add Resource to planet
			Clean,              # Remove all empty fleets
			Heal,               # Repair any ships orbiting a friendly planet
			Defeat,             # Remove overlords if a player has no more units
			Win,                # Figure out if there is any winner
			SyncDB,             # Synchronizes the Research Database with the CSV files
			Turn,               # Increase the Universe's "Turn" value
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
			
			# Design Categories are added so Players can check designs ingame.
			c = Category()
			c.name = "Fighter"
			c.desc = "Those who fight"
			c.insert()
			c = Category()
			c.name = "Bomber"
			c.desc = "Those who bomb"
			c.insert()
			c = Category()
			c.name = "Capital Ship"
			c.desc = "Those who capital?"
			c.insert()
			
			c = Category()
			c.name = 'Drones'
			c.desc = 'Drone Components'
			c.insert()
			
			#Overlord Design definition allows fleets to show if an overlord is in that fleet.
			d = Design()
			d.id = 0
			d.name = 'Overlord'
			d.categories = []
			d.components = []
			d.owner = -1
			d.desc = "Master and Commander of your forces"
			d.insert()
			
			
			
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

	def populate(self,  numPlanets , maptype = 'random', numPlayers = 2, seed=None, loadfile = None,):
		"""\
		--populate <game>  <number of Planets> <maximunum number of players> <Map Type> <seed> <load file>
		    Maptypes so far can be standard and random
		    Number of Planets includes player planets
		    
		    seed can be set for purposes of saved games. But fully random seeds are also allowed by typing in None
		    a loadfile does not need to be specified unless it is a loaded map.
		"""


		numPlanets = int(numPlanets)
		numPlayers = int(numPlayers)
		maptype = maptype.lower()

		if numPlanets < numPlayers:
			print "Invalid: Number of Players cannot be more than then number of total planets"
			return

		dbconn.use(self.game)

		trans = dbconn.begin()
		
		if len(Object.bytype('tp.server.rules.dronesec.objects.Planet')) > 0:
			print "Game has already been populated. Cannot populate more than once"
			return

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
				# A "Balanced" map would be equal for all players in game
				size = SIZE * numPlanets * numPlayers
				divisions = (2.0 * math.pi)/numPlayers
				planetsPerDivision = int(math.floor(numPlanets / numPlayers))
				# Extra planets that cannot be arranged equally for all players have some special rules.
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

				# If Only one planet is remaining then just dump it in the very center of the universe.
				# Otherwise, make a randomly placed "circle" of as many planets as they can fit.
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

					self.addPlanet(r, n, posx, posy, posz)

			elif maptype == 'load':
				if loadfile == None:
					print "Cannot populate game as no file was given"
					return
				self.loadMap(loadfile, r)

			else: #maptype =='random': 
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
			# Get all planets that a player can be assigned to.
			homeplanets = Object.bytype('tp.server.rules.dronesec.objects.Planet')
			homeplanets = [id for (id, time) in homeplanets if Object(id).playerhome and Object(id).owner == -1]
			
			if len(homeplanets) == 0:
				print "Sorry but the amount of players for this map has been reached"
				return


			user = RulesetBase.player(self, username, password, email, comment)

			#First player created will always start at the same position should game be replayed
			r = random.Random()
			if self.seed == None:
				r.seed(self.seed)
			else:
				r.seed(self.seed + user.id)
			

			# Randomly select a player's home planet and assign it to him
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

			# Create Player lists for research and drone availability
			players = Player()
			players.BuildList()
			players.insert()

			print "%s has been assigned Planet: %s" % (username, planet.name)

			trans.commit()

			return (user, planet, overlord)
		except:
			trans.rollback()
			raise

	def loadMap(self, fileName, r):
		"""\
		Loads an xml file and creates planets according to the given specifications.
		"""
		import xml.etree.ElementTree as ET
		import os
		tree = ET.parse(os.path.join(os.path.abspath("./tp/server/rules/dronesec/maps/"),fileName))
		universe = tree.getroot()
		for planet in universe:
			# FIXME: There is probably a much faster way of doing this
			# This only occurs once a game so its not critical.
			name = planet.find('Name').text.strip()
			x = planet.find('posx').text.strip()
			y = planet.find('posy').text.strip()
			z = planet.find('posz').text.strip()
			if planet.find('size') != None:
				size = planet.find('size').text.strip()
			else:
				size = -1
			if planet.find('home') != None:
				home = True
			else:
				home = False
			self.addPlanet(r, name, int(x), int(y), int(z), int(size), home)

	def addPlanet(self, r, name, x, y, z , size =-1 ,home = False):
		"""\
		Creates a system and a planet according to the given positions.
		"""


		#tpclient-pywx only has graphics for systems so in order to "see" the map systems have to be created.
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
