#!/usr/bin/env python

from abc import ABCMeta, abstractmethod

from tp.server.model import Model

class Ruleset( object ):#{{{
	"""
	Rulesets define how gameplay works.
	"""
	__metaclass__ = ABCMeta

	name    = "Unknown Ruleset"
	version = 'Unknown Version'

	def __init__( self, game ):
		"""
		Initialise a ruleset.
		"""
		self.game = game

	@property
	def model( self ):
		return self.game.model
	
	@abstractmethod
	def loadModelConstants( self ):
		"""
		Adds classes to the Model which represents immutable data for a
		ruleset.
		"""
		from tp.server.model import ( ObjectType, OrderType, ObjectOrder,
				ResourceType )

		self.model.add_class( ObjectType )
		self.model.add_class( OrderType )
		self.model.add_class( ObjectOrder, 'ObjectType', 'OrderType' )
		self.model.add_class( ResourceType )

	@abstractmethod
	def initModelConstants( self ):
		"""
		This method initialises all data which is considered to be constant for
		a ruleset lifetime.
		"""
		ObjectType = self.model.use( 'ObjectType' )

		Model.add( ObjectType( id = _1, name = _2 )
				for _1, _2 in enumerate( self.__ObjectType__ ))

		OrderType = self.model.use( 'OrderType' )

		Model.add( OrderType( id = _1, name = _2 )
				for _1, _2 in enumerate( self.__OrderType__ ))

		ObjectOrder = self.model.use( 'ObjectOrder' )

		ObjectOrderList = []

		for ObjectName, OrderNameList in self.__ObjectOrder__.iteritems():
			for OrderName in OrderNameList:
				ObjectOrderList.append( ( ObjectType.ByName( ObjectName ), OrderType.ByName( OrderName ) ) )

		Model.add( ObjectOrder( object_type = _1, order_type = _2 )
				for _1, _2 in ObjectOrderList )

	@abstractmethod
	def loadModel( self ):
		"""
		Adds classes to the Model which represents mutable data for a ruleset.
		"""
		from tp.server.model import ( Parameter, Player, Object, Board,
				Reference, Component, Property, Category,
				Message, Order, Design, MessageReference, ComponentCategory,
				ComponentProperty, DesignCategory, DesignComponent,
				DesignProperty, PropertyCategory, ObjectParameter,
				OrderParameter )

		self.model.add_class( Player )
		self.model.add_class( Reference )
		self.model.add_class( Component )
		self.model.add_class( Property )
		self.model.add_class( Object, 'ObjectType' )
		self.model.add_class( Category, 'Player' )
		self.model.add_class( Board, 'Player' )
		self.model.add_class( Design, 'Player' )
		self.model.add_class( Message, 'Board' )
		self.model.add_class( Order, 'OrderType', 'Object' )
		self.model.add_class( MessageReference, 'Message', 'Reference' )
		self.model.add_class( ComponentCategory, 'Component', 'Category' )
		self.model.add_class( ComponentProperty, 'Component', 'Property' )
		self.model.add_class( DesignCategory, 'Design', 'Category' )
		self.model.add_class( DesignComponent, 'Design', 'Component' )
		self.model.add_class( DesignProperty, 'Design', 'Property' )
		self.model.add_class( PropertyCategory, 'Property', 'Category' )

		self.model.add_class( Parameter )
		self.model.add_class( ObjectParameter, 'Object', 'Parameter' )
		self.model.add_class( OrderParameter, 'Order', 'Parameter' )

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
		return "%s, version %s" % ( self.name, self.version )
#}}}

__all__ = [ 'Ruleset' ]
