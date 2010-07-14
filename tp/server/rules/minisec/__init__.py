#!/usr/bin/env python

from tp.server.db import DatabaseManager
from tp.server.bases import Vector3D

# Generic Actions
from tp.server.rules.base import Ruleset as RulesetBase
from tp.server.rules.base.orders import WaitOrder, MergeFleetOrder, ColoniseOrder
from tp.server.rules.base.actions import Move, Clean, Win

# Minisec specific imports
from tp.server.rules.minisec.orders import MoveOrder, BuildFleetOrder, SplitFleetOrder
from tp.server.rules.minisec.actions import FleetCombat, Heal, Turn

from random import Random

class Ruleset( RulesetBase ):#{{{
	"""
	Minisec Ruleset...
	"""
	name    = "Minisec"
	version = "0.0.1"

	# The order orders and actions occur
	orderOfOrders = [
			BuildFleetOrder, 			# Build all ships
			MergeFleetOrder, 			# Merge fleets together
			SplitFleetOrder, 			# Split any fleets - this means you can merge then split in one turn
			Clean, 						# Clean up fleets which no longer exist
			(MoveOrder, 'prepare'),		# Set the velocity of objects
			Move, 						# Move all the objects about
			(MoveOrder, 'finalise'),	# Check for objects which may have overshot the destination
			FleetCombat, 				# Perform a combat, ships may have escaped by moving away
			ColoniseOrder, 				# Colonise any planets, ships may have been destoryed or reached their destination
			Clean, 						# Remove all empty fleets
			Heal, 						# Repair any ships orbiting a friendly planet
			Win, 						# Figure out if there is any winner
			WaitOrder, 					# Wait needs to occur last
			Turn, 						# Increase the Universe's "Turn" value
	]

	def __init__( self, game ):
		super( Ruleset, self ).__init__( game )

		self.random = Random()
		self.SIZE   = 10000000
		self.SPEED  = 300000000

	def load( self ):
		from tp.server.rules.base.objects import Universe, Galaxy, StarSystem, Planet, Wormhole, Fleet
		from tp.server.rules.minisec.objects import Ship

		objs = self.game.objects

		Object, Player = objs.use( 'Object', 'Player' )

		objs.add_object_class( Universe )
		objs.add_object_class( Galaxy )
		objs.add_object_class( StarSystem )
		objs.add_object_class( Planet )
		objs.add_object_class( Fleet )
		objs.add_object_class( Wormhole )

		objs.add_order_class( WaitOrder )
		objs.add_order_class( MergeFleetOrder )
		objs.add_order_class( ColoniseOrder )
		objs.add_order_class( MoveOrder )
		objs.add_order_class( BuildFleetOrder )
		objs.add_order_class( SplitFleetOrder )

		objs.add_class( Ship, 'Design' )

		from tp.server.rules.base.parameters import ( AbsCoordParam, TimeParam,
				ObjectParam, PlayerParam, NumberParam, StringParam,
				ResourceQuantity, ResourceQuantityParam, DesignQuantity,
				DesignQuantityParam )

		objs.add_class( DesignQuantity, 'Parameter', 'Design' )
		objs.add_class( ResourceQuantity, 'Parameter', 'ResourceType' )

		objs.add_parameter_class( AbsCoordParam )
		objs.add_parameter_class( TimeParam )
		objs.add_parameter_class( ObjectParam, 'Object' )
		objs.add_parameter_class( PlayerParam, 'Player' )
		objs.add_parameter_class( NumberParam )
		objs.add_parameter_class( StringParam )
		objs.add_parameter_class( DesignQuantityParam, 'DesignQuantity' )
		objs.add_parameter_class( ResourceQuantityParam, 'ResourceQuantity' )

	def createUniverse( self, name ):
		Universe = self.game.objects.use( 'Universe' )

		return Universe( name = name, size = self.SIZE, age = 0 )

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
		Fleet, Design, DesignQuantity = self.game.objects.use( 'Fleet', 'Design', 'DesignQuantity' )

		return Fleet(
				parent   = parent,
				size     = 3,
				name     = name,
				ships    = [ DesignQuantity( design = Design.ByName('Frigate'), quantity = 3 ) ],
				damage   = 0,
				position = parent.position,
				owner    = owner)

	def initialise( self ):
		RulesetBase.initialise( self )

		universe = self.createUniverse( name = "The Universe" )

		Design, Ship = self.game.objects.use( 'Design', 'Ship' )

		scout_design = Design(
				name		= "Scout",
				description	= "N/A" )

		frigate_design = Design(
				name		= "Frigate",
				description	= "N/A" )

		battleship_design = Design(
				name		= "Battleship",
				description	= "N/A" )

		scout = Ship(
				design			= scout_design,
				hp				= 2,
				primary_damage	= 0,
				backup_damage	= 0,
				speed 			= 3 * self.SPEED,
				build_time		= 1 )

		frigate = Ship(
				design			= frigate_design,
				hp 				= 4,
				primary_damage	= 2,
				backup_damage	= 0,
				speed			= 2 * self.SPEED,
				build_time		= 2 )

		battleship = Ship(
				design			= battleship_design,
				hp				= 6,
				primary_damage	= 3, 
				backup_damage	= 1,
				speed			= 1 * self.SPEED,
				build_time		= 4 )

		with DatabaseManager().session() as session:
			session.add( universe )

			session.add( scout_design )
			session.add( frigate_design )
			session.add( battleship_design )

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
			session.add( universe )
			session.add( system )
			session.add( planet )
			session.add( fleet )

		return ( user, system, planet, fleet )
#}}}

__all__ = [ 'Ruleset' ]
