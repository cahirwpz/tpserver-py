#!/usr/bin/env python

"""
Classes for dealing with games hosted on the machine.
"""

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref

from SQL import Enum, SQLBase, SelectableByName

class Lock( SQLBase ):#{{{
	"""
	Each server can add different types of locks to each game.

	The following lock types are supported:
		Serving    - This program is serving the database.
		Processing - This program is processing a turn.
	"""
	LockTypes = ['serving', 'processing']

	@classmethod
	def InitMapper( cls, metadata, Game ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',	   Integer, index = True, primary_key = True),
				Column('type',     Enum( cls.LockTypes ), nullable = False ),  # The type of lock
				Column('game_id',  Game( Game.id ), nullable = True ),         # On which game the lock acquired
				Column('hostname', String(255), nullable = False,
					default = socket.gethostname() ),                          # Hostname of the process is running on
				Column('pid',      Integer, nullable = False,
					default = os.getpid()),                                    # PID of the process with the lock
				Column('mtime',	   DateTime, nullable = False,                 # Last time the lock was updated
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		mapper( cls, cls.__table__, properties = {
			'game': relation( Game,
				uselist = False,
				backref = backref( 'locks' ))
			})

	def __str__( self ):
		return '<Lock id="%s" game="%s" host="%s" pid="%s">' % ( self.id, self.game.name, self.type, self.hostname, self.pid ) 
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
	__types__ = ['shutdown', 'endofturn', 'gameadded', 'gameremoved', 'gameupdated']

	@classmethod
	def InitMapper( cls, metadata, Game ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',      Integer, index = True, primary_key = True),
				Column('game_id', ForeignKey( Game.id ), nullable = True),
				Column('type',    Enum( cls.__types__ ), nullable = False),
				Column('mtime',   DateTime, nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		mapper( cls, cls.__table__, properties = {
			'game': relation( Game,
				uselist = False,
				backref = backref( 'events' ))
			})

	def __str__(self):
		return '<Event id="%s" game="%s" type="%s">' % ( self.id, self.game.name, self.type ) 
#}}}

class ConnectionEvent( SQLBase ):#{{{
	"""
	Events regarding connections get recorded in this table.

	The following event types are supported:
		connect    - A connection is made from an IP address.
		login      - A person logs in on the connection.
		disconnect - A connection is terminated.
	"""
	__types__ = ['connect', 'login', 'disconnect']

	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',	Integer, index = True, primary_key = True),
				Column('ip',    String(255), nullable = False),
				Column('type',  Enum( cls.__types__ ), nullable = False),
				Column('mtime',	DateTime, nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		mapper( cls, cls.__table__ )

	def __str__(self):
		return '<ConnectionEvent id="%s" type="%s" ip="%s">' % ( self.id, self.type, self.ip ) 
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
	
	def __str__(self):
		return '<Game id="%s" name="%s" turn="%s">' % ( self.id, self.name, self.turn )
#}}}

__all__ = [ 'Game', 'ConnectionEvent', 'GameEvent', 'Lock' ]
