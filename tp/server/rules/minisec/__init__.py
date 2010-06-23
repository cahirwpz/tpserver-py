#!/usr/bin/env python

from tp.server.utils import ReparentOne
from tp.server.db import DatabaseManager

from tp.server.bases import Object

# Generic Actions
from tp.server.rules.base import Ruleset as RulesetBase
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
import actions.Turn as Turn

import random

SIZE = 10000000

class Ruleset(RulesetBase):#{{{
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
			Turn, 				# Increase the Universe's "Turn" value
	]

	def initialise(self, game):
		"""
		Minisec 
		"""
		RulesetBase.initialise(self)

		# Need to create the top level universe object...
		universe = game.Object()
		universe.id		= 0
		universe.type	= 'tp.server.rules.base.objects.Universe'
		universe.name   = "The Universe"
		universe.size   = SIZE
		universe.turn   = 0

		with DatabaseManager().session() as session:
			session.add( universe )

	def populate(self, seed, system_min, system_max, planet_min, planet_max):
		"""
		--populate <game> <random seed> <min systems> <max systems> <min planets> <max planets>
		
			Populate a universe with a number of systems and planets.
			The number of systems in the universe is dictated by min/max systems.
			The number of planets per system is dictated by min/max planets.
		"""
		seed, system_min, system_max, planet_min, planet_max = (int(seed), int(system_min), int(system_max), int(planet_min), int(planet_max))

		with DatabaseManager().session() as session:
			# FIXME: Assuming that the Universe and the Galaxy exist.
			r = random.Random()
			r.seed(int(seed))

			# Create this many systems
			for i in range(0, r.randint(system_min, system_max)):
				pos = r.randint(SIZE*-1, SIZE)*1000, r.randint(SIZE*-1, SIZE)*1000, r.randint(SIZE*-1, SIZE)*1000
				
				# Add system
				system = self.game.Object()
				system.type = 'tp.server.rules.base.objects.System'
				system.name = "System %s" % i
				system.size = r.randint(800000, 2000000)
				system.posx = pos[0]
				system.posy = pos[1]
				# ReparentOne(system) ??
				session.add( system )
				session.commit()

				print "Created system (%s)" % system.name
				
				# In each system create a number of planets
				for j in range(0, r.randint(planet_min, planet_max)):
					planet = self.game.Object()
					planet.type = 'tp.server.rules.base.objects.Planet'
					planet.name = "Planet %i in %s" % (j, system.name)
					planet.size = r.randint(1000, 10000)
					planet.parent_id = system.id
					planet.posx = pos[0]+r.randint(1,100)*1000
					planet.posy = pos[1]+r.randint(1,100)*1000
					session.add( planet )

					print "Created planet (%s)" % planet.name

	def player(self, username, password, email='Unknown', comment='A Minisec Player'):
		"""
		Create a Solar System, Planet, and initial Fleet for the player, positioned randomly within the Universe.
		"""
		user   = RulesetBase.player(self, username, password, email, comment)
		system = None
		planet = None
		fleet  = None

		with DatabaseManager().session() as session:
			# FIXME: Hack! This however means that player x will always end up in the same place..
			r = random.Random()
			r.seed(user.id)

			pos = r.randint(SIZE*-1, SIZE)*1000, r.randint(SIZE*-1, SIZE)*1000, r.randint(SIZE*-1, SIZE)*1000

			system = self.game.Object()
			system.type='tp.server.rules.base.objects.System'
			system.name = "%s Solar System" % username
			system.parent = 0
			system.size = r.randint(800000, 2000000)
			(system.posx, system.posy, junk) = pos
			#ReparentOne(system)
			system.owner = user.id

			session.add( system )

			planet = self.game.Object()
			planet.type='tp.server.rules.base.objects.Planet'
			planet.name = "%s Planet" % username
			planet.parent = system.id
			planet.size = 100
			planet.posx = system.posx+r.randint(1,100)*1000
			planet.posy = system.posy+r.randint(1,100)*1000
			planet.owner = user.id

			session.add( planet )

			fleet = self.game.Object()
			fleet.type='tp.server.rules.minisec.objects.Fleet'
			fleet.parent = planet.id
			fleet.size = 3
			fleet.name = "%s First Fleet" % username
			fleet.ships = {1:3}
			(fleet.posx, fleet.posy, fleet.posz) = (planet.posx, planet.posy, planet.posz)
			fleet.owner = user.id

			session.add( fleet )

		return (user, system, planet, fleet)
#}}}
