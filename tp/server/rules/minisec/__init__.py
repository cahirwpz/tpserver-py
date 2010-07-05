#!/usr/bin/env python

from tp.server.db import DatabaseManager
from tp.server.bases import Vector3D

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

from random import Random

class Ruleset( RulesetBase ):#{{{
	"""
	Minisec Ruleset...
	"""
	name    = "Minisec"
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

	def __init__( self, game ):
		super( Ruleset, self ).__init__( game )

		self.random = Random()
		self.SIZE   = 10000000
		self.SPEED  = 300000000


	def load( self ):
		from tp.server.bases.objects import Universe, Galaxy, StarSystem, Planet, Wormhole
		from tp.server.rules.minisec.objects import Resource, Fleet, Ship, FleetComposition

		objs = self.game.objects

		Object, Player = objs.use( 'Object', 'Player' )

		objs.add_object_class( Universe )
		objs.add_object_class( Galaxy )
		objs.add_object_class( StarSystem )
		objs.add_object_class( Planet, 'Player' )
		objs.add_object_class( Fleet, 'Player' )
		objs.add_object_class( Wormhole )

		objs.add_class( Ship )
		objs.add_class( FleetComposition, 'Fleet', 'Ship' )
		objs.add_class( Resource, 'Planet', 'ResourceType' )

	def createUniverse( self, name ):
		Universe = self.game.objects.use( 'Universe' )

		return Universe( name = name, size = self.SIZE )

	def createStarSystem( self, parent, name ):
		StarSystem = self.game.objects.use( 'StarSystem' )

		return StarSystem(
				name		= name,
				parent		= parent,
				position	= Vector3D( self.random.randint(-self.SIZE, self.SIZE) * 1000,
										self.random.randint(-self.SIZE, self.SIZE) * 1000),
				size		= self.random.randint(800000, 2000000))

	def createPlanet( self, parent, name, owner = None ):
		Planet = self.game.objects.use( 'Planet' )

		return Planet(
				name		= name,
				parent		= parent,
				position	= Vector3D( parent.position.x + self.random.randint(1, 100) * 1000,
										parent.position.y + self.random.randint(1, 100) * 1000),
				size		= self.random.randint(1000, 10000),
				owner		= owner)

	def createFleet( self, parent, name, owner = None):
		Fleet, Ship, FleetComposition = self.game.objects.use( 'Fleet', 'Ship', 'FleetComposition' )

		return Fleet(
				parent   = parent,
				size     = 3,
				name     = name,
				ships    = [ FleetComposition( ship = Ship.ByName('Frigate'), number = 3 ) ],
				position = parent.position,
				owner    = owner)

	def initialise( self ):
		RulesetBase.initialise( self )

		with DatabaseManager().session() as session:
			universe = self.createUniverse( name = "The Universe" )

			session.add( universe )

			Ship = self.game.objects.use( 'Ship' )

			scout = Ship(
					name			= "Scout",
					hp				= 2,
					primary_damage	= 0,
					backup_damage	= 0,
					speed 			= 3 * self.SPEED )

			frigate = Ship(
					name			= "Frigate",
					hp 				= 4,
					primary_damage	= 2,
					backup_damage	= 0,
					speed			= 2 * self.SPEED )

			battleship = Ship(
					name			= "Battleship",
					hp				= 6,
					primary_damage	= 3, 
					backup_damage	= 1,
					speed			= 1 * self.SPEED )

			session.add( scout )
			session.add( frigate )
			session.add( battleship )

	def populate(self, seed, system_min, system_max, planet_min, planet_max):
		"""
			Populate a universe with a number of systems and planets.
			The number of systems in the universe is dictated by min/max systems.
			The number of planets per system is dictated by min/max planets.
		"""
		seed, system_min, system_max, planet_min, planet_max = (int(seed), int(system_min), int(system_max), int(planet_min), int(planet_max))

		Object = self.game.objects.use( 'Object' )

		universe = Object.ByType( 'Universe' )[-1]

		with DatabaseManager().session() as session:
			# FIXME: Assuming that the Universe and the Galaxy exist.
			self.random.seed( int(seed) )

			# Create this many systems
			for i in range( self.random.randint( system_min, system_max ) ):
				system = self.createStarSystem( parent = universe, name = "System %s" % i )
				session.add( system )
				
				# In each system create a number of planets
				for j in range( self.random.randint( planet_min, planet_max ) ):
					session.add( self.createPlanet( parent = system, name = "Planet %i in %s" % (j, system.name) ) )

	def player( self, username, password, email = 'Unknown', comment = 'A Minisec Player' ):
		"""
		Create a Solar System, Planet, and initial Fleet for the player, positioned randomly within the Universe.
		"""
		user = super( Ruleset, self ).player( username, password, email, comment )

		# FIXME: Hack! This however means that player x will always end up in the same place..
		self.random.seed( user.id )

		Object = self.game.objects.use( 'Object' )

		universe	= Object.ByType( 'Universe' )[-1]
		system		= self.createStarSystem( parent = universe, name = "%s Solar System" % username )
		planet		= self.createPlanet( parent = system, name = "%s Planet" % username, owner = user )
		fleet		= self.createFleet( parent = planet, name = "%s First Fleet" % username, owner = user )

		with DatabaseManager().session() as session:
			session.add( system )
			session.add( planet )
			session.add( fleet )

		return ( user, system, planet, fleet )
#}}}

__all__ = [ 'Ruleset' ]
