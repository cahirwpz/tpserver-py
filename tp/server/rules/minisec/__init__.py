#!/usr/bin/env python

from tp.server.db import DatabaseManager, make_dependant_mapping, make_parametrized_mapping
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
		metadata = DatabaseManager().metadata

		from tp.server.bases.objects import UniverseClass, GalaxyClass, StarSystemClass, PlanetClass, WormholeClass
		from tp.server.rules.minisec.objects import Resource, FleetClass, Ship, FleetComposition

		game = self.game

		Object = game.Object

		game.Universe			= make_parametrized_mapping( UniverseClass( Object ),	metadata, Object )
		game.Galaxy   			= make_parametrized_mapping( GalaxyClass( Object ),		metadata, Object )
		game.StarSystem			= make_parametrized_mapping( StarSystemClass( Object ),	metadata, Object )
		game.Planet				= make_parametrized_mapping( PlanetClass( Object ),		metadata, Object, game.Player )
		game.Fleet				= make_parametrized_mapping( FleetClass( Object ),		metadata, Object, game.Player )
		game.Wormhole			= make_parametrized_mapping( WormholeClass( Object ),	metadata, Object )
		game.Ship 				= make_dependant_mapping( Ship, metadata, game )
		game.FleetComposition	= make_dependant_mapping( FleetComposition, metadata, game, game.Fleet, game.Ship )
		game.Resource			= make_dependant_mapping( Resource, metadata, game, game.Planet, game.ResourceType )

	def createUniverse( self, name ):
		universe = self.game.Universe()
		universe.name = name
		universe.size = self.SIZE

		return universe

	def createStarSystem( self, parent, name ):
		system = self.game.StarSystem()
		system.name     = name
		system.parent   = parent
		system.position = Vector3D(
				self.random.randint(-self.SIZE, self.SIZE) * 1000,
				self.random.randint(-self.SIZE, self.SIZE) * 1000,
				0 )
		system.size     = self.random.randint(800000, 2000000)
		
		return system

	def createPlanet( self, parent, name, owner = None ):
		planet = self.game.Planet()
		planet.name     = name
		planet.parent   = parent
		planet.position = Vector3D(
				parent.position.x + self.random.randint(1, 100) * 1000,
				parent.position.y + self.random.randint(1, 100) * 1000,
				0 )
		planet.size     = self.random.randint(1000, 10000)
		planet.owner    = owner

		return planet

	def createFleet( self, parent, name, owner = None):
		fleet = self.game.Fleet()
		fleet.parent   = parent
		fleet.size     = 3
		fleet.name     = name
		fleet.ships    = [ self.game.FleetComposition( ship = self.game.Ship.ByName('Frigate'), number = 3 ) ]
		fleet.position = parent.position
		fleet.owner    = owner

		return fleet

	def initialise( self ):
		RulesetBase.initialise( self )

		with DatabaseManager().session() as session:
			universe = self.createUniverse( name = "The Universe" )

			session.add( universe )

			Ship = self.game.Ship

			SPEED = 30000000

			scout = Ship( name = "Scout",
					hp = 2,
					primary_damage = 0,
					backup_damage = 0,
					speed = 3 * self.SPEED )

			frigate = Ship( name = "Frigate",
					hp = 4,
					primary_damage = 2,
					backup_damage = 0,
					speed = 2 * self.SPEED )

			battleship = Ship( name = "Battleship",
					hp = 6,
					primary_damage = 3, 
					backup_damage = 1,
					speed = 1 * self.SPEED )

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

		universe = self.game.Object.ByType( 'Universe' )[-1]

		with DatabaseManager().session() as session:
			# FIXME: Assuming that the Universe and the Galaxy exist.
			self.random.seed( int(seed) )

			# Create this many systems
			for i in range(0, self.random.randint(system_min, system_max)):
				system = self.createStarSystem( parent = universe, name = "System %s" % i )
				session.add( system )
				
				# In each system create a number of planets
				for j in range(0, self.random.randint(planet_min, planet_max)):
					session.add( self.createPlanet( parent = system, name = "Planet %i in %s" % (j, system.name) ) )

	def player(self, username, password, email='Unknown', comment='A Minisec Player'):
		"""
		Create a Solar System, Planet, and initial Fleet for the player, positioned randomly within the Universe.
		"""
		user   = super( Ruleset, self ).player(username, password, email, comment)
		system = None
		planet = None
		fleet  = None

		universe = self.game.Object.ByType( 'Universe' )[-1]

		with DatabaseManager().session() as session:
			# FIXME: Hack! This however means that player x will always end up in the same place..
			self.random.seed( user.id )

			system = self.createStarSystem( parent = universe, name = "%s Solar System" % username )
			session.add( system )

			planet = self.createPlanet( parent = system, name = "%s Planet" % username, owner = user )
			session.add( planet )

			fleet = self.createFleet( parent = planet, name = "%s First Fleet" % username, owner = user )
			session.add( fleet )

		return (user, system, planet, fleet)
#}}}

__all__ = [ 'Ruleset' ]
