#!/usr/bin/env python

from sqlalchemy import *

from tp.server.db import *
from Game import Game
from SQL import SQLBase, SQLUtils

class PlayerUtils( SQLUtils ):#{{{
	def realid(self, user, id):
		if id == 0:
			return user.id
		else:
			return id

	def usernameid(self, game, username, password = None):
		"""
		Get the id for a user given a game, username and password.
		"""

		session = DatabaseManager().session()

		if password is None:
			result = session.query( self.cls ).filter_by( username = username ).first()
		else:
			result = session.query( self.cls ).filter_by( username = username, password = password ).first()
		
		if result:
			return result.id
		else:
			return -1

	def getPlayer(self, game, username, password = None):
		"""
		Get the id for a user given a game, username and password.
		"""

		session = DatabaseManager().session()

		if password is None:
			return session.query( self.cls ).filter_by( username = username ).first()
		else:
			return session.query( self.cls ).filter_by( username = username, password = password ).first()

	@staticmethod
	def split(username):
		"""
		Split a username into the user and game parts.
		"""
		if username.find('@') == -1:
			raise TypeError('The given username is not valid...')
		
		return username.split('@', 1)
#}}}

class Player( SQLBase ):#{{{
	Utils = PlayerUtils()

	@classmethod
	def getTable( cls, name, metadata ):
		return Table( name, metadata,
				Column('id',	    Integer,     index = True, primary_key = True),
				Column('username',  String(255), nullable = False, ),
				Column('password',  String(255), nullable = False, ),
				Column('comment',   Binary,      nullable = False, default = ""),
				Column('mtime',	    DateTime,    nullable = False,
					onupdate = func.current_timestamp(),
					default = func.current_timestamp()),
				UniqueConstraint('username'))

	def __str__(self):
		return "<Player id=%s username=%s>" % (self.id, self.username)

	@property
	def game(self):
		return self.__game.id

	@game.setter
	def game(self, value):
		if hasattr(self, '__game'):
			raise TypeError('The game can not be changed!')
		self.__game = Game(id=value)

	@property
	def playing(self):
		return bool(self.__game)
#}}}

__all__ = [ 'Player' ]
