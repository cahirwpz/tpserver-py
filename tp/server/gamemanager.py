import sqlalchemy.exc

from tp.server.db import DatabaseManager, make_mapping, make_dependant_mapping
from tp.server.bases import *
from tp.server.logging import msg, logctx
from tp.server.singleton import SingletonClass

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

		metadata = DatabaseManager().metadata

		for cls in [ make_mapping( Game, metadata ),
					 make_mapping( ConnectionEvent, metadata ),
					 make_mapping( GameEvent, metadata, Game.__tablename__ ) ]:
			cls.__table__.create( checkfirst = True )

		self.game = {}

		with DatabaseManager().session() as session:
			for g in session.query( Game ).all():
				g.load()

				self.game[ g.name ] = g

	def addGame( self, name, longname, rulesetname, admin, comment ):
		if self.game.has_key( name ):
			raise AlreadyExists( "Game '%s' already exists!" % name )

		g = Game( ruleset_name = rulesetname, name = name, longname = longname, admin = admin, comment = comment )

		with DatabaseManager().session() as session:
			session.add( g )

		g.load()
		g.createTables()

		self.game[ name ] = g
	
	def removeGame( self, name ):
		if not self.game.has_key( name ):
			raise NoSuchThing( "Game '%s' does not exists!" % name )
		
		self.game[ name ].createTables()
		self.game[ name ].dropTables()

		with DatabaseManager().session() as session:
			session.delete( self.game[ name ] )

		del self.game[ name ]
		
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
