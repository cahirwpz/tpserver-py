from tp.server.db import DatabaseManager, make_mapping, make_dependant_mapping
from tp.server.bases import *
from tp.server.logging import msg, logctx
from tp.server.singleton import SingletonClass
class ThousandParsecGame( object ):
	def __init__( self, game ):
		self.game = game

		with DatabaseManager().metadata() as metadata:
			self.Player  			= make_dependant_mapping( Player,				metadata, game )
			self.Object  			= make_dependant_mapping( Object,				metadata, game )
			self.Order   			= make_dependant_mapping( Order,				metadata, game, self.Object.__tablename__ )
			self.Board				= make_dependant_mapping( Board,				metadata, game )
			self.Reference			= make_dependant_mapping( Reference,			metadata, game )
			self.Lock				= make_dependant_mapping( Lock,					metadata, game )

			self.Component			= make_dependant_mapping( Component,			metadata, game )
			self.Property			= make_dependant_mapping( Property,				metadata, game )
			self.Resource			= make_dependant_mapping( Resource,				metadata, game )
			self.Category			= make_dependant_mapping( Category,				metadata, game )

			self.Design				= make_dependant_mapping( Design,				metadata, game, self.Player.__tablename__ )
			self.Message			= make_dependant_mapping( Message,				metadata, game, self.Board.__tablename__ )
			self.MessageReference	= make_dependant_mapping( MessageReference,		metadata, game, self.Message.__tablename__, self.Reference.__tablename__ )
			self.ComponentCategory	= make_dependant_mapping( ComponentCategory,	metadata, game, self.Component.__tablename__, self.Category.__tablename__ )
			self.ComponentProperty	= make_dependant_mapping( ComponentProperty,	metadata, game, self.Component.__tablename__, self.Property.__tablename__ )
			self.DesignCategory		= make_dependant_mapping( DesignCategory,		metadata, game, self.Design.__tablename__, self.Category.__tablename__ )
			self.DesignComponent	= make_dependant_mapping( DesignComponent,		metadata, game, self.Design.__tablename__, self.Component.__tablename__ )
			self.PropertyCategory	= make_dependant_mapping( PropertyCategory,		metadata, game, self.Property.__tablename__, self.Category.__tablename__ )
	
	def initialise( self ):
		self.game.ruleset.initialise(self)
	
	def populate( self ):
		self.game.ruleset.initialise(self, 0xdeadc0de, 10, 10, 2, 2)

class GameManager( object ):
	__metaclass__ = SingletonClass

	def __init__( self ):
		# Remove any order mapping from the network libray...
		#PacketFactory().objects.OrderDescs().clear()

		#self.events = Event.latest()

		# Register all the games..
		#self.locks  = []

		#for _id, _time in Game.ids():
		#	self.onGameAdded( Game( _id ) )

		with DatabaseManager().metadata() as metadata:
			make_mapping( Game, metadata )
			make_mapping( ConnectionEvent, metadata )
			make_mapping( GameEvent, metadata, Game.__tablename__ )

		self.game = {}

		with DatabaseManager().session() as session:
			for game in session.query( Game ).all():
				self.game[ game.shortname ] = None

		self.addGame( 'minisec', 'tp', 'Test Game', 'admin@localhost' )

	def addGame( self, rulesetname, shortname, longname, admin ):
		g = Game()
		g.ruleset_name = rulesetname
		g.name_short   = shortname
		g.name_long    = longname
		g.admin       = admin

		with DatabaseManager().session() as session:
			session.add( g )

			self.game[ g.name_short ] = ThousandParsecGame( g )

		self.game[ shortname ].initialise()
		self.game[ shortname ].populate()
	
	def startZeroconf( self ):
		pass

	def stopZeroconf( self ):
		pass

	@logctx
	def poll( self ):
		# Get any new events..
		for event in Event.since(self.events):
			msg( 'New Event: %s' % event )

			if hasattr(self, event.eventtype):
				try:
					getattr(self, event.eventtype)(Game(event.game))
				except Exception, ex:
					msg( str(ex) )
			
			self.events = event.id

	def onGameAdded(self, game):
		already = [lock.game for lock in self.locks]

		if game.id in already:
			msg( "Got onGameAdded event for a game I already have a lock on!" )
			return

		# Create a lock for this game
		db.dbconn.use( game )
		self.locks.append( Lock.new('serving') )
		db.dbconn.commit()

		# Setup the game
		game.ruleset.setup()

		# TODO: Add game to ZeroConf

	def onGameRemoved( self, game ):
		toremove = None

		for lock in self.locks:
			if lock.game == game.id:
				toremove = lock
				break
		
		if toremove is None:
			msg( "Got onGameRemoved event for a game I didn't have a lock on!" )
			return

		# TODO: Remove game from ZeroConf
			
		self.locks.remove(toremove)

		del toremove

		db.dbconn.commit()

		msg( "Game removed: %s" % game )

	def endOfTurn(self, game):
		# Send TimeRemaining Packets to all users belonging to game
		packet = PacketFactory().objects.TimeRemaining(0, -1)

	def shutdown( self ):
		# Remove the locks
		del self.locks

		self.stopZeroconf()

	def logPrefix( self ):
		return self.__class__.__name__
