#!/usr/bin/env python

from abc import ABCMeta, abstractmethod
from random import Random

from tp.server.model import Model

class RulesetUniverseGenerator( object ):
	def __init__( self, ruleset ):
		self.ruleset = ruleset
		self.random  = Random()

	def initialise( self, seed, system_min, system_max, planet_min, planet_max ):
		self.random.seed( seed )

		self.system_min = system_min
		self.system_max = system_max
		self.planet_min = planet_min
		self.planet_max = planet_max

	@property
	def model( self ):
		return self.ruleset.model

	@property
	def SIZE( self ):
		return 10**7
	
	@property
	def SPEED( self ):
		return 3 * 10**8 

	@property
	def randint( self ):
		return self.random.randint

class RulesetModelLoader( object ):
	__metaclass__ = ABCMeta

	def __init__( self, ruleset ):
		self.ruleset = ruleset

	@property
	def model( self ):
		return self.ruleset.model

	@abstractmethod
	def loadModelConstants( self ):
		pass

	@abstractmethod
	def initModelConstants( self ):
		pass

	@abstractmethod
	def loadModel( self ):
		pass

class RulesetParameters( RulesetModelLoader ):
	from tp.server.rules.base.parameters import ( AbsCoordParam, TimeParam,
			ObjectParam, PlayerParam, RelCoordParam, RangeParam,
			StringParam, NumberParam, ResourceQuantityParam,
			DesignQuantityParam )

	ParameterTypeMap = {
			  0 : [ AbsCoordParam ],
			  1 : [ TimeParam ],
			  2 : [ ObjectParam, 'Object' ],
			  3 : [ PlayerParam, 'Player' ],
			  4 : [ RelCoordParam, 'Object' ],
			  5 : [ RangeParam ],
			# 6 : [ ListParam ],
			  7 : [ StringParam ],
			# 8 : [ GenericReference ],
			# 9 : [ GenericReferenceList ],
			 -1 : [ NumberParam ],
			 -2 : [ DesignQuantityParam, 'DesignQuantity' ],
			 -3 : [ ResourceQuantityParam, 'ResourceQuantity' ] }

	def loadModelConstants( self ):
		from tp.server.model import ParameterType

		self.model.add_class( ParameterType )

	def initModelConstants( self ):
		ParameterType = self.model.use( 'ParameterType' )

		Model.add( ParameterType( id = _1, name = _2[0].__name__ )
				for _1, _2 in self.ParameterTypeMap.items() )
	
	def loadModel( self ):
		from tp.server.model import ( Parameter, OrderParameter, ObjectParameter )

		self.model.add_class( Parameter, 'ParameterType' )
		self.model.add_class( OrderParameter, 'Order', 'Parameter' )
		self.model.add_class( ObjectParameter, 'Object', 'Parameter' )

		from tp.server.rules.base.parameters import ( DesignQuantity,
				ResourceQuantity )

		self.model.add_class( DesignQuantity, 'Parameter', 'Design' )
		self.model.add_class( ResourceQuantity, 'Parameter', 'ResourceType' )

		for type_id, args in self.ParameterTypeMap.items():
			self.model.add_parameter_class( args[0], type_id, *args[1:] )

class RulesetReferences( RulesetModelLoader ):
	ReferenceTypeMap = {
			-1000 : 'ServerAction',
			   -5 : 'DesignAction',
			   -4 : 'PlayerAction',
			   -3 : 'MessageAction',
			   -2 : 'OrderAction',
			   -1 : 'ObjectAction',
				0 : 'Misc',
				1 : 'Object',
				2 : 'OrderType',
				3 : 'Order',
				4 : 'Board',
				5 : 'Message',
				6 : 'ResourceType',
				7 : 'Player',
				8 : 'Category',
				9 : 'Design',
			   10 : 'Component',
			   11 : 'Property',
			   12 : 'ObjectType',
			   13 : 'OrderQueue' }

	def loadModelConstants( self ):
		from tp.server.model import ReferenceType

		self.model.add_class( ReferenceType )

	def initModelConstants( self ):
		ReferenceType = self.model.use( 'ReferenceType' )

		Model.add( ReferenceType( id = _1, name = _2 )
				for _1, _2 in self.ReferenceTypeMap.items() )

	def loadModel( self ):
		from tp.server.model import Reference

		self.model.add_class( Reference, 'ReferenceType' )

class RulesetObjects( RulesetModelLoader ):
	ObjectTypes = []

	def loadModelConstants( self ):
		from tp.server.model import ObjectType

		self.model.add_class( ObjectType )

	def initModelConstants( self ):
		ObjectType = self.model.use( 'ObjectType' )

		Model.add( ObjectType( id = _1, name = _2.__name__ )
				for _1, _2 in enumerate( self.ObjectTypes ))
	
	def loadModel( self ):
		from tp.server.model import Object

		self.model.add_class( Object, 'ObjectType' )

		for ObjectType in self.ObjectTypes:
			self.model.add_object_class( ObjectType )

class RulesetOrders( RulesetModelLoader ):
	OrderTypes   = []
	ObjectOrders = {}

	def loadModelConstants( self ):
		from tp.server.model import ( OrderType, ObjectOrder )

		self.model.add_class( OrderType )
		self.model.add_class( ObjectOrder, 'ObjectType', 'OrderType' )

	def initModelConstants( self ):
		ObjectType, OrderType, ObjectOrder = self.model.use( 'ObjectType', 'OrderType', 'ObjectOrder' )

		Model.add( OrderType( id = _1, name = _2.__name__ )
				for _1, _2 in enumerate( self.OrderTypes ))

		ObjectOrderList = []

		for ObjectName, OrderNameList in self.ObjectOrders.iteritems():
			for _1 in OrderNameList:
				ObjectOrderList.append( ( ObjectType.ByName( ObjectName ), OrderType.ByName( _1.__name__ ) ) )

		Model.add( ObjectOrder( object_type = _1, order_type = _2 )
				for _1, _2 in ObjectOrderList )

	def loadModel( self ):
		from tp.server.model import Order

		self.model.add_class( Order, 'OrderType', 'Object', 'Player' )

		for OrderType in self.OrderTypes:
			self.model.add_order_class( OrderType )

class Ruleset( object ):
	"""
	Rulesets define how gameplay works.
	"""
	__metaclass__ = ABCMeta

	name    = "Unknown Ruleset"
	version = 'Unknown Version'

	RulesetUniverseGeneratorClass = None
	RulesetObjectsClass           = None
	RulesetOrdersClass            = None
	RulesetActionProcessorClass   = None

	def __init__( self, game ):
		"""
		Initialise a ruleset.
		"""
		self.game = game

		self.generator = self.RulesetUniverseGeneratorClass( self )
		self.processor = self.RulesetActionProcessorClass( self )

		self.modelLoaders = [
				self.RulesetObjectsClass( self ),
				self.RulesetOrdersClass( self ),
				RulesetParameters( self ),
				RulesetReferences( self ) ]

	@property
	def model( self ):
		return self.game.model
	
	def loadModelConstants( self ):
		"""
		Adds classes to the Model which represents immutable data for a
		ruleset.
		"""
		for loader in self.modelLoaders:
			loader.loadModelConstants()

	def initModelConstants( self ):
		"""
		This method initialises all data which is considered to be constant for
		a ruleset lifetime.
		"""
		Model.create( self.model )

		for loader in self.modelLoaders:
			loader.initModelConstants()

	@abstractmethod
	def loadModel( self ):
		"""
		Adds classes to the Model which represents mutable data for a ruleset.
		"""
		from tp.server.model import ( Player, Board, Component, Property,
				Category, Message, Design, ComponentCategory,
				ComponentProperty, DesignCategory, DesignComponent,
				DesignProperty, PropertyCategory, ResourceType )

		self.model.add_class( Player )
		self.model.add_class( Component )
		self.model.add_class( Property )
		self.model.add_class( ResourceType )
		self.model.add_class( Category, 'Player' )
		self.model.add_class( Board, 'Player' )
		self.model.add_class( Design, 'Player' )
		self.model.add_class( Message, 'Board' )
		self.model.add_class( ComponentCategory, 'Component', 'Category' )
		self.model.add_class( ComponentProperty, 'Component', 'Property' )
		self.model.add_class( DesignCategory, 'Design', 'Category' )
		self.model.add_class( DesignComponent, 'Design', 'Component' )
		self.model.add_class( DesignProperty, 'Design', 'Property' )
		self.model.add_class( PropertyCategory, 'Property', 'Category' )

		for loader in self.modelLoaders:
			loader.loadModel()

	@abstractmethod
	def initModel( self ):
		""" 
		Initialise the database with anything needed for this game.

		The ruleset should do things like,
			- Create any components in the databases
			- Create any resources in the databases
			- etc

		This should not add anything to the players universe. Use the populate
		command for that.

		This command takes no arguments, so it should not do anything which 
		needs information from the user.
		"""
		Model.create( self.model )
	
	def resetModel( self ):
		for name in [ 'Board', 'Object', 'Design', 'Component', 'Property', 'ResourceType', 'Category', 'Player' ]:
			Object = self.model.use( name )

			Model.remove( Object.query().all() )

	@abstractmethod
	def populate( self, *args, **kwargs ):
		"""
		Populate the "universe". It is given a list of arguments.

		All arguments should be documented in the doc string.
		"""

	@abstractmethod
	def addPlayer( self, username, password, email = 'N/A', comment = '' ):
		"""
		Create a player for this game.

		The default function creates a new user, a board for the user and adds a
		welcome message. It returns the newly created user object.
		"""
		Player, Board, Message = self.model.use( 'Player', 'Board', 'Message' )

		player = Player(
			username	= username,
			password	= password,
			email		= email,
			comment		= comment)

		board = Board(
			owner		= player,
			name        = "Private message board for %s" % username,
			description = "This board is used so that stuff you own (such as fleets and planets) can inform you of what is happening in the universe.")

		board.messages.append(
			Message(
				subject = "Welcome to the Universe!",
				body    = "Welcome, %s, to the python Thousand Parsec server. Hope you have fun!" \
						  "This game is currently playing version %s of %s." % ( username, self.version, self.name ),
				turn    = self.game.turn ))

		Model.add( player, board )

		return player

	@property
	def information( self ):
		return [ ( 'name',    self.name ),
				 ( 'version', self.version ),
				 ( 'comment', "\n".join( map( str.strip, self.__doc__.strip().splitlines() ))) ]
	
	def __str__( self ):
		return '<%s version="%s">' % ( self.__class__.__name__, self.version )

__all__ = [ 'Ruleset', 'RulesetObjects', 'RulesetOrders', 'RulesetUniverseGenerator' ]
