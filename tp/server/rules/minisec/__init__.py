#!/usr/bin/env python

from tp.server.model import Vector3D, Model

# Generic Actions
from tp.server.rules.base import Ruleset
from tp.server.rules.base.orders import WaitOrder, MergeFleetOrder, ColoniseOrder
from tp.server.rules.base.actions import MoveAction, CleanAction, WinAction

# Minisec specific imports
from tp.server.rules.minisec.orders import MoveOrder, BuildFleetOrder, SplitFleetOrder
from tp.server.rules.minisec.actions import FleetCombatAction, HealAction, TurnAction

from random import Random

class MinisecRuleset( Ruleset ):#{{{
	"""
	Minisec Ruleset...
	"""
	name    = "Minisec"
	version = "0.0.1"

	# The order orders and actions occur
	OrderOfOrders = [
			BuildFleetOrder, 			# Build all ships
			MergeFleetOrder, 			# Merge fleets together
			SplitFleetOrder, 			# Split any fleets - this means you can merge then split in one turn
			CleanAction, 				# Clean up fleets which no longer exist
			(MoveOrder, 'prepare'),		# Set the velocity of objects
			MoveAction, 				# Move all the objects about
			(MoveOrder, 'finalise'),	# Check for objects which may have overshot the destination
			FleetCombatAction,			# Perform a combat, ships may have escaped by moving away
			ColoniseOrder, 				# Colonise any planets, ships may have been destoryed or reached their destination
			CleanAction, 				# Remove all empty fleets
			HealAction,					# Repair any ships orbiting a friendly planet
			WinAction, 					# Figure out if there is any winner
			WaitOrder, 					# Wait needs to occur last
			TurnAction, 				# Increase the Universe's "Turn" value
			]

	__ObjectOrder__ = {
			'Fleet'  : ['WaitOrder','MoveOrder','SplitFleetOrder','MergeFleetOrder','ColoniseOrder'],
			'Planet' : ['WaitOrder','BuildFleetOrder'] }

	__ObjectType__ = ['Universe','Galaxy','StarSystem','Planet','Fleet','Wormhole']

	__OrderType__ = ['WaitOrder','MergeFleetOrder','ColoniseOrder','MoveOrder','BuildFleetOrder','SplitFleetOrder']

	def __init__( self, game ):
		Ruleset.__init__( self, game )

		self.random = Random()
		self.SIZE   = 10000000
		self.SPEED  = 300000000

	def loadModelConstants( self ):
		Ruleset.loadModelConstants( self )

	def initModelConstants( self ):
		Ruleset.initModelConstants( self )

	def loadModel( self ):
		Ruleset.loadModel( self )

		from tp.server.rules.base.objects import Universe, Galaxy, StarSystem, Planet, Wormhole, Fleet
		from tp.server.rules.minisec.objects import Ship

		self.model.add_object_class( Universe )
		self.model.add_object_class( Galaxy )
		self.model.add_object_class( StarSystem )
		self.model.add_object_class( Planet )
		self.model.add_object_class( Fleet )
		self.model.add_object_class( Wormhole )

		self.model.add_order_class( WaitOrder )
		self.model.add_order_class( MergeFleetOrder )
		self.model.add_order_class( ColoniseOrder )
		self.model.add_order_class( MoveOrder )
		self.model.add_order_class( BuildFleetOrder )
		self.model.add_order_class( SplitFleetOrder )

		self.model.add_class( Ship, 'Design' )

		from tp.server.rules.base.parameters import ( AbsCoordParam,
				RelCoordParam, TimeParam, ObjectParam, PlayerParam,
				NumberParam, StringParam, ResourceQuantity,
				ResourceQuantityParam, DesignQuantity, DesignQuantityParam )

		self.model.add_class( DesignQuantity, 'Parameter', 'Design' )
		self.model.add_class( ResourceQuantity, 'Parameter', 'ResourceType' )

		self.model.add_parameter_class( AbsCoordParam )
		self.model.add_parameter_class( RelCoordParam, 'Object' )
		self.model.add_parameter_class( TimeParam )
		self.model.add_parameter_class( ObjectParam, 'Object' )
		self.model.add_parameter_class( PlayerParam, 'Player' )
		self.model.add_parameter_class( NumberParam )
		self.model.add_parameter_class( StringParam )
		self.model.add_parameter_class( DesignQuantityParam, 'DesignQuantity' )
		self.model.add_parameter_class( ResourceQuantityParam, 'ResourceQuantity' )
	
	def createUniverse( self, name ):
		Universe = self.model.use( 'Universe' )

		return Universe( name = name, size = self.SIZE, age = 0 )

	def createStarSystem( self, parent, name ):
		StarSystem = self.model.use( 'StarSystem' )

		return StarSystem(
				name		= name,
				parent		= parent,
				position	= Vector3D( self.random.randint(-self.SIZE, self.SIZE) * 1000,
										self.random.randint(-self.SIZE, self.SIZE) * 1000),
				size		= self.random.randint(800000, 2000000))

	def createPlanet( self, parent, name, owner = None ):
		Planet = self.model.use( 'Planet' )

		return Planet(
				name		= name,
				parent		= parent,
				position	= Vector3D( parent.position.x + self.random.randint(1, 100) * 1000,
										parent.position.y + self.random.randint(1, 100) * 1000),
				size		= self.random.randint(1000, 10000),
				owner		= owner)

	def createFleet( self, parent, name, owner = None):
		Fleet, Design, DesignQuantity = self.model.use( 'Fleet', 'Design', 'DesignQuantity' )

		return Fleet(
				parent   = parent,
				size     = 3,
				name     = name,
				ships    = [ DesignQuantity( design = Design.ByName('Frigate'), quantity = 3 ) ],
				damage   = 0,
				position = parent.position,
				owner    = owner)

	def initModel( self ):
		Ruleset.initModel( self )

		universe = self.createUniverse( name = "The Universe" )

		Design, Ship = self.model.use( 'Design', 'Ship' )

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

		Model.add( universe, scout_design, frigate_design, battleship_design,
				scout, frigate, battleship )

	def populate( self, seed, system_min, system_max, planet_min, planet_max ):
		"""
			Populate a universe with a number of systems and planets.
			The number of systems in the universe is dictated by min/max systems.
			The number of planets per system is dictated by min/max planets.
		"""
		Ruleset.populate( self, seed, system_min, system_max, planet_min, planet_max )

		Object = self.model.use( 'Object' )

		universe = Object.ByType( 'Universe' )[0]

		# FIXME: Assuming that the Universe and the Galaxy exist.
		self.random.seed( int(seed) )

		objs = []

		# Create this many systems
		for i in range( self.random.randint( system_min, system_max ) ):
			system = self.createStarSystem( parent = universe, name = "System %s" % i )
			objs.append( system )
			
			# In each system create a number of planets
			for j in range( self.random.randint( planet_min, planet_max ) ):
				objs.append( self.createPlanet( parent = system, name = "Planet %i in %s" % (j, system.name) ) )

		Model.add( objs )

	def addPlayer( self, username, password, email = 'Unknown', comment = 'A Minisec Player' ):
		"""
		Create a Solar System, Planet, and initial Fleet for the player, positioned randomly within the Universe.
		"""
		user = Ruleset.addPlayer( self, username, password, email, comment )

		# FIXME: Hack! This however means that player x will always end up in the same place..
		self.random.seed( user.id )

		Object = self.model.use( 'Object' )

		universe	= Object.ByType( 'Universe' )[0]
		system		= self.createStarSystem( parent = universe, name = "%s Solar System" % username )
		planet		= self.createPlanet( parent = system, name = "%s Planet" % username, owner = user )
		fleet		= self.createFleet( parent = planet, name = "%s First Fleet" % username, owner = user )

		Model.add( universe, system, planet, fleet )

		return ( user, system, planet, fleet )
#}}}

__all__ = [ 'MinisecRuleset' ]
