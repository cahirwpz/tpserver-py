#!/usr/bin/env python

"""
Classes for dealing with games hosted on the machine.
"""

from collections import Mapping

from sqlalchemy import *
from sqlalchemy.orm import mapper

from tp.server.rules import RulesetManager
from tp.server.db import DatabaseManager, make_dependant_mapping
from tp.server.db.enum import Enum
from SQL import SQLBase, SelectableByName

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

class ObjectManager( Mapping ):#{{{
	def __init__( self ):
		self.__objects = {}

	def add( self, name, cls ):
		self.__objects[ name ] = cls

		setattr( self, name, cls )

	def use( self, *names ):
		if len( names ) == 1:
			return self.__objects[ names[0] ]
		else:
			return tuple( self.__objects[ name ] for name in names )

	def __getitem__( self, name ):
		return self.__objects[ name ]

	def __len__( self ):
		return self.__objects.__len__()

	def __iter__( self ):
		return self.__objects.__iter__()
#}}}

class Game( SQLBase, SelectableByName ):#{{{
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

		# hack to prevent warnings about nonexisiting attributes
		object.__setattr__( self, '_Game__ruleset', None )
		object.__setattr__( self, 'objects', ObjectManager() )

	def load( self ):
		from tp.server.bases import Player, Object, Board, Reference, Lock, 	\
			Component, Property, ResourceType, Category, Message, Slot, Order,	\
			Design, MessageReference, ComponentCategory, ComponentProperty, 	\
			DesignCategory, DesignComponent, PropertyCategory

		objs = self.objects

		objs.add('Player',				make_dependant_mapping( Player,				self ))
		objs.add('Object',				make_dependant_mapping( Object,				self ))
		objs.add('Reference',			make_dependant_mapping( Reference,			self ))
		objs.add('Lock',				make_dependant_mapping( Lock,				self ))
		objs.add('Component',			make_dependant_mapping( Component,			self ))
		objs.add('Property',			make_dependant_mapping( Property,			self ))
		objs.add('ResourceType',		make_dependant_mapping( ResourceType,		self ))
		objs.add('Category',			make_dependant_mapping( Category,			self ))
		objs.add('Message',				make_dependant_mapping( Message,			self ))
		objs.add('Board',				make_dependant_mapping( Board,				self, objs.Player ))
		objs.add('Slot',				make_dependant_mapping( Slot,				self, objs.Board, objs.Message ))
		objs.add('Order',				make_dependant_mapping( Order,				self, objs.Object ))
		objs.add('Design',				make_dependant_mapping( Design,				self, objs.Player ))
		objs.add('MessageReference',	make_dependant_mapping( MessageReference,	self, objs.Message, objs.Reference ))
		objs.add('ComponentCategory',	make_dependant_mapping( ComponentCategory,	self, objs.Component, objs.Category ))
		objs.add('ComponentProperty',	make_dependant_mapping( ComponentProperty,	self, objs.Component, objs.Property ))
		objs.add('DesignCategory',		make_dependant_mapping( DesignCategory,		self, objs.Design, objs.Category ))
		objs.add('DesignComponent',		make_dependant_mapping( DesignComponent,	self, objs.Design, objs.Component ))
		objs.add('PropertyCategory',	make_dependant_mapping( PropertyCategory,	self, objs.Property, objs.Category ))

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
