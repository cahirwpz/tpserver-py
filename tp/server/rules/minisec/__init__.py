#!/usr/bin/env python

from tp.server.model import Vector3D, Model

# Generic Actions
from tp.server.rules.base import Ruleset, RulesetObjects, RulesetOrders, RulesetUniverseGenerator, ActionProcessor
from tp.server.rules.base.orders import WaitOrder, MergeFleetOrder, ColoniseOrder
from tp.server.rules.base.actions import MoveAction, CleanAction, WinAction

# Minisec specific imports
from tp.server.rules.minisec.orders import MoveOrder, BuildFleetOrder, SplitFleetOrder
from tp.server.rules.minisec.actions import FleetCombatAction, HealAction, TurnAction

class MinisecUniverseGenerator( RulesetUniverseGenerator ):
	def createUniverse( self, name ):
		Universe = self.model.use( 'Universe' )

		return Universe(
				name = name,
				size = self.SIZE,
				age  = 0 )

	def createStarSystem( self, parent, name ):
		StarSystem = self.model.use( 'StarSystem' )

		return StarSystem(
				name		= name,
				parent		= parent,
				position	= Vector3D( self.randint(-self.SIZE, self.SIZE) * 1000,
										self.randint(-self.SIZE, self.SIZE) * 1000),
				size		= self.randint(800000, 2000000))

	def createPlanet( self, parent, name, owner = None ):
		Planet = self.model.use( 'Planet' )

		return Planet(
				name		= name,
				parent		= parent,
				position	= Vector3D( parent.position.x + self.randint(1, 100) * 1000,
										parent.position.y + self.randint(1, 100) * 1000),
				size		= self.randint(1000, 10000),
				owner		= owner)

	def createFleet( self, parent, name, owner = None ):
		Fleet, Design = self.model.use( 'Fleet', 'Design' )

		return Fleet(
				parent   = parent,
				size     = 3,
				name     = name,
				ships    = { Design.ByName('Frigate') : 3 },
				damage   = 0,
				position = parent.position,
				owner    = owner)

	def generateStarSystems( self, parent ):
		return [ self.createStarSystem( parent = parent, name = "System %s" % i )
				for i in range( self.randint( self.system_min, self.system_max ) ) ]
	
	def generatePlanets( self, parent ):
		return [ self.createPlanet( parent = parent, name = "Planet %i in %s" %	(j, parent.name) )
				for j in range( self.randint( self.planet_min, self.planet_max ) ) ]
	
	def createShipClasses( self ):
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

		return [ scout, frigate, battleship ]

class MinisecActionProcessor( ActionProcessor ):
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

class MinisecObjects( RulesetObjects ):
	from tp.server.rules.base.objects import Universe, Galaxy, StarSystem, Planet, Wormhole, Fleet
		
	ObjectTypes = [ Universe, Galaxy, StarSystem, Planet, Fleet, Wormhole ]

class MinisecOrders( RulesetOrders ):
	OrderTypes = [ WaitOrder, MergeFleetOrder, ColoniseOrder, MoveOrder, BuildFleetOrder, SplitFleetOrder ]

	ObjectOrders = {
			'Fleet'  : [ WaitOrder, MoveOrder, SplitFleetOrder, MergeFleetOrder, ColoniseOrder ],
			'Planet' : [ WaitOrder, BuildFleetOrder ] }

class MinisecRuleset( Ruleset ):
	"""
	Minisec Ruleset...
	"""
	name    = "minisec"
	version = "0.0.1"

	RulesetUniverseGeneratorClass = MinisecUniverseGenerator
	RulesetObjectsClass           = MinisecObjects
	RulesetOrdersClass            = MinisecOrders
	RulesetActionProcessorClass   = MinisecActionProcessor

	def loadModel( self ):
		Ruleset.loadModel( self )

		from tp.server.rules.minisec.objects import Ship

		self.model.add_class( Ship, 'Design' )

	def initModel( self ):
		Ruleset.initModel( self )

		universe = self.generator.createUniverse( name = "The Universe" )
		ships    = self.generator.createShipClasses()

		Model.add( universe, ships )

	def populate( self, *args, **kwargs ):
		"""
		Populate a universe with a number of systems and planets.
		"""
		Ruleset.populate( self, *args, **kwargs )

		self.generator.initialise( *args )

		Object = self.model.use( 'Object' )

		universe = Object.ByType( 'Universe' )[0]

		systems = self.generator.generateStarSystems( parent = universe )

		for system in systems:
			self.generator.generatePlanets( parent = system )

		Model.update( universe )

	def addPlayer( self, username, password, email = 'Unknown', comment = 'A Minisec Player' ):
		"""
		Create a Solar System, Planet, and initial Fleet for the player, positioned randomly within the Universe.
		"""
		user = Ruleset.addPlayer( self, username, password, email, comment )

		Object = self.model.use( 'Object' )

		universe	= Object.ByType( 'Universe' )[0]
		system		= self.generator.createStarSystem( parent = universe, name = "%s Solar System" % username )
		planet		= self.generator.createPlanet( parent = system, name = "%s Planet" % username, owner = user )
		fleet		= self.generator.createFleet( parent = planet, name = "%s First Fleet" % username, owner = user )

		Model.add( universe, system, planet, fleet )

		return ( user, system, planet, fleet )

__all__ = [ 'MinisecRuleset', 'MinisecUniverseGenerator' ]
