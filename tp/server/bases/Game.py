#!/usr/bin/env python

"""
Classes for dealing with games hosted on the machine.
"""

from sqlalchemy import *
from sqlalchemy.orm import mapper

from tp.server.rules import RulesetManager
from tp.server.db import DatabaseManager, make_dependant_mapping
from tp.server.db.enum import Enum
from SQL import SQLBase

# FIXME: There should be some way to store the ruleset parameters...

class Lock( SQLBase ):#{{{
	"""
	Each server can add different types of locks to each game.

	The following lock types are supported:
		Serving    - This program is serving the database.
		Processing - This program is processing a turn.
	"""
	LockTypes = ['serving', 'processing']

	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',	    Integer, index = True, primary_key = True),
				Column('lock_type', Enum(cls.LockTypes), nullable = False ),		# Locktype
				Column('hostname',  String(255), nullable = False ),				# Hostname of the process is running on
				Column('pid',       Integer, nullable = False ), 					# PID of the process with the lock
				Column('mtime',	    DateTime, nullable = False,						# Last time the lock was updated
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		mapper( cls, cls.__table__ )

#{{{
	#@classmethod
	#def new(cls, type):
	#	"""
	#	Create a new lock of the given type.
	#
	#	When a lock goes out of scope it will remove itself from the database.
	#	"""
	#	self = cls()
	#	self.local = True
	#
	#	if not type in Lock.types:
	#		raise TypeError('Lock type can only be one of %s' % Lock.types)
	#
	#	self.locktype = unicode(type)
	#	self.pid      = os.getpid()
	#	self.host     = socket.gethostname()
	#	self.save()
	#	msg( "Creating lock %s %s" % ( self, hasattr(self, 'local') and self.local ) )
	#	return self

	#def __del__(self):
	#	if hasattr(self, 'id'):
	#		if hasattr(self, 'local') and self.local:
	#			dbconn.use(self.game)
	#			msg( "Removing lock %s %s" %  ( self, hasattr(self, 'local') and self.local ) )
	#			self.remove()

	#@staticmethod
	#def locked(type, game=None):
	#	t = Lock.table
	#	if game is None:
	#		return len(dbconn.execute(select([t.c.id], t.c.locktype==type)).fetchall()) > 0
	#	else:
	#		return len(dbconn.execute(select([t.c.id], (t.c.locktype==type)&(t.c.game==game.id))).fetchall()) > 0

	#@staticmethod
	#def cleanup():
	#	t = Lock.table
	#	dbconn.execute(delete(t, t.c.host == socket.gethostname()))
	#	# locallocks = dbconn.execute(select([t.c.game, t.c.id, t.c.pid, t.c.locktype], t.c.host==socket.gethostname())).fetchall()
	#	# for gid, id, pid, locktype in locallocks:
	#	#	msg( "%s-%s %s %s" % (gid, id pid, locktype ) )
#}}}

	def __str__( self ):
		try:
			id = self.id
		except AttributeError:
			id = '(new)'

		return "<Lock-%s,%s %s by %s-%s>" % ( id, self.__game__, self.lock_type, self.hostname, self.pid ) 
#}}}

class GameEvent( SQLBase ):#{{{
	"""
	Sometimes 'Events' occur. This table stores them.

	When a server starts up it reads the latest event id from the table. 
	It then checks periodicly that no id greater then the current on has been
	added to the table.

	Events can be the following types,
		Shutdown      - Shutdown of a given game is requested (normally before deletion or upgrade).
		End of Turn   - An end of turn has occurred.

		Game Added    - A new game is added.
		Game Removed  - A game is removed.
		Game Updated  - Information about a game is updated.
	"""
	EventTypes = ['shutdown', 'endofturn', 'gameadded', 'gameremoved', 'gameupdated']

	@classmethod
	def InitMapper( cls, metadata, Game ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',	     Integer, index = True, primary_key = True),
				Column('game',	     ForeignKey( Game.id ), nullable = True),
				Column('event_type', Enum( cls.EventTypes ), nullable = False),
				Column('mtime',	     DateTime, nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		mapper( cls, cls.__table__ )

#{{{
	# @classmethod
	# def new(cls, eventtype, game=None):
	#	if not eventtype in Event.types:
	#		raise TypeError("Event type must be %r not %s" % (cls.types, eventtype))
	#
	#	# Create a new event object
	#	if game != None and not isinstance(game, (Game, int, long)):
	#		raise TypeError("Second argument must be an ID or a game object not %r!" % game)
	#
	#	e = Event()
	#	e.eventtype	= eventtype
	#	e.game		= game
	#
	#	if isinstance(game, (Game, NoneType)):
	#		e.game = game.id
	#
	#	old = dbconn.use(None)
	#	e.insert()
	#	dbconn.use(old)
	#	return e

	# @classmethod
	# def latest(cls):
	#	"""
	#	Get the lates Event id.
	#	"""
	#	old = dbconn.use(None)
	#	try:
	#		c = cls.table.c
	#		try:
	#			return select([c.id], order_by=[desc(c.id)], limit=1).execute().fetchall()[0][0]
	#		except IndexError:
	#			return -1
	#	finally:
	#		dbconn.use(old)

	# @classmethod
	# def since(cls, id):
	#	"""
	#	Get all events since a given id.
	#	"""
	#	old = dbconn.use(None)
	#
	#	try:
	#		dbconn.use(None)
	#		c = cls.table.c
	#		return [Event(id=x['id']) for x in select([c.id], c.id>id, order_by=[asc(c.id)]).execute()]
	#	finally:
	#		dbconn.use(old)
#}}} 

	def __str__(self):
		try:
			_id = self.id
		except AttributeError:
			_id = '(new)'

		return "<Event-%s (Game - %s) %s>" % (_id, self.game, self.eventtype) 
#}}}

class ConnectionEvent( SQLBase ):#{{{
	"""
	Events regarding connections get recorded in this table.

	The following event types are supported:
		connect    - A connection is made from an IP address.
		login      - A person logs in on the connection.
		disconnect - A connection is terminated.
	"""
	EventTypes = ['connect', 'login', 'disconnect']

	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',	     Integer,     index = True, primary_key = True),
				Column('ip',         String(255), nullable = False),
				Column('event_type', Enum(cls.EventTypes), nullable = False),
				Column('mtime',	     DateTime,    nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		mapper( cls, cls.__table__ )
#}}}

class Game( SQLBase ):#{{{
	"""
	This class represents games which exist on the server. Only one instance exists for each game.
	"""

	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',			Integer,		index = True,	    primary_key = True),
				Column('name',	        String(255),	nullable = False),						# Computer name
				Column('longname',		Text,			nullable = False,	default	= ""),		# Human readable name
				Column('ruleset_name',	String(255),	nullable = False),						# Ruleset this game uses
				Column('admin',			String(255),	nullable = False),						# Admin's email address
				Column('comment',		Text,			nullable = False,	default	= ""),		# A generic comment
				Column('turn',			Integer,		nullable = False,   default = 0),		# The current turn of the game
				Column('mtime',			DateTime,		nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()),
				UniqueConstraint('name'))

		mapper( cls, cls.__table__ )
	
	def __init__( self, **kwargs ):
		super( Game, self ).__init__( **kwargs )

		object.__setattr__( self, '_Game__ruleset', None )

	def load( self ):
		base = __import__( 'tp.server.bases', globals(), locals(), [
				'Player', 'Object', 'Board', 'Reference', 'Lock', 'Component',
				'Property', 'ResourceType', 'Category', 'Message', 'Slot', 'Order',
				'Design', 'MessageReference', 'ComponentCategory',
				'ComponentProperty', 'DesignCategory', 'DesignComponent',
				'PropertyCategory' ], -1 )

		metadata = DatabaseManager().metadata

		self.Player  			= make_dependant_mapping( base.Player,				metadata, self )
		self.Object  			= make_dependant_mapping( base.Object,				metadata, self )
		self.Board				= make_dependant_mapping( base.Board,				metadata, self )
		self.Reference			= make_dependant_mapping( base.Reference,			metadata, self )
		self.Lock				= make_dependant_mapping( base.Lock,				metadata, self )
		self.Component			= make_dependant_mapping( base.Component,			metadata, self )
		self.Property			= make_dependant_mapping( base.Property,			metadata, self )
		self.ResourceType		= make_dependant_mapping( base.ResourceType,		metadata, self )
		self.Category			= make_dependant_mapping( base.Category,			metadata, self )
		self.Message			= make_dependant_mapping( base.Message,				metadata, self )

		self.Slot				= make_dependant_mapping( base.Slot,				metadata, self, self.Board, self.Message )
		self.Order   			= make_dependant_mapping( base.Order,				metadata, self, self.Object )
		self.Design				= make_dependant_mapping( base.Design,				metadata, self, self.Player )
		self.MessageReference	= make_dependant_mapping( base.MessageReference,	metadata, self, self.Message, self.Reference )
		self.ComponentCategory	= make_dependant_mapping( base.ComponentCategory,	metadata, self, self.Component, self.Category )
		self.ComponentProperty	= make_dependant_mapping( base.ComponentProperty,	metadata, self, self.Component, self.Property )
		self.DesignCategory		= make_dependant_mapping( base.DesignCategory,		metadata, self, self.Design, self.Category )
		self.DesignComponent	= make_dependant_mapping( base.DesignComponent,		metadata, self, self.Design, self.Component )
		self.PropertyCategory	= make_dependant_mapping( base.PropertyCategory,	metadata, self, self.Property, self.Category )

		self.ruleset.load()

	def createTables( self ):
		metadata = DatabaseManager().metadata

		tables = list( metadata.tables )

		for table in tables:
			if table.startswith( "%s_" % self.name ):
				metadata.tables[ table ].create( checkfirst = True )
	
	def dropTables( self ):
		metadata = DatabaseManager().metadata

		tables = list( metadata.tables )

		for table in tables:
			if table.startswith( "%s:" % self.name ):
				metadata.tables[ table ].drop()
				del metadata.tables[ table ]
	
	def initialise( self ):
		self.ruleset.initialise()
	
	def populate( self ):
		self.ruleset.initialise(self, 0xdeadc0de, 10, 10, 2, 2)
	
	@classmethod
	def ByName( cls, name ):
		result = None

		with DatabaseManager().session() as session:
			result = session.query( cls ).filter_by( name = name ).first()

		return result

	@property
	def ruleset(self):
		"""
		Return the Ruleset (object) this game uses.
		""" 
		if self.__ruleset is None:
			if not hasattr(self, 'ruleset_name'):
				raise RuntimeError('No ruleset assigned to this game!')

			self.__ruleset = RulesetManager()[ self.ruleset_name ]( self )

		return self.__ruleset

	@ruleset.setter
	def ruleset(self, name):
		if hasattr(self, 'ruleset_name'):
			raise RuntimeError('A ruleset can only be set once!')

		self.__ruleset = RulesetManager()[ name ]( self )

		self.ruleset_name = name

#{{{
	# @staticmethod
	# def munge(game):
	#	"""
	#	Convert a longname into some sort of suitable short name.
	#	"""
	#	return game.replace(' ', '').strip().lower()

	# @property
	# def key(self):
	#	# FIXME: This probably isn't very secure...
	#	key = hashlib.md5("%s-%s" % (self.longname, self.time))
	#	return key.hexdigest()

	# @property
	# def players(self):
	#	from User import User
	#	dbconn.use(self)
	#	return User.amount()

	# @property
	# def objects(self):
	#	from Object import Object
	#	dbconn.use(self)
	#	return Object.amount()

	# @property
	# def parameters(self):
	#	return dict(
	#			plys	= self.players,
	#			# cons: Number of clients currently connected
	#			objs	= self.objects,
	#			admin	= self.admin,
	#			cmt		= self.comment,
	#			# next: Unix timestamp (GMT) when next turn is generated
	#			ln		= self.longname,
	#			sn		= self.short,
	#			turn	= self.turn
	#			# prd: The time between turns in seconds.
	#		)
#}}}

	def __str__(self):
		if hasattr(self, 'id'):
			return "<Game-%i %s (%s) turn-%i>" % (self.id, self.name, self.longname, self.turn)
		else:
			return "<Game-(new) %s (%s) turn-%i>" % (self.name, self.longname, self.turn)
#}}}

__all__ = [ 'Game', 'ConnectionEvent', 'GameEvent', 'Lock' ]
