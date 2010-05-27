"""
Resources require to build stuff.
"""

from sqlalchemy import *

from tp.server.db import *
from tp.server.bases.Game import Game
from tp.server.bases.SQL import SQLBase, SQLUtils

class UserUtils( SQLUtils ):#{{{
	def realid(self, user, id):
		if id == 0:
			return user.id
		else:
			return id

	def usernameid(self, game, username, password=None):
		"""
		Get the id for a user given a game, username and password.
		"""
		dbconn.use(game)

		t = self.cls.table
		if password != None:
			result = select([t.c.id], (t.c.username==username) & (t.c.password==password)).execute().fetchall()
		else:
			result = select([t.c.id], (t.c.username==username)).execute().fetchall()
		
		if len(result) != 1:
			return -1
		else:
			return result[0]['id']

	@staticmethod
	def split(username):
		"""
		Split a username into the user and game parts.
		"""
		if username.find('@') == -1:
			raise TypeError('The given username is not valid...')
		
		return username.split('@', 1)
#}}}

class User( SQLBase ):#{{{
	Utils = UserUtils()

	table = Table('user', metadata,
				Column('game', 	    Integer,     nullable=False, index=True, primary_key=True),
				Column('id',	    Integer,     nullable=False, index=True, primary_key=True),
				Column('username',  String(255), nullable=False, index=True),
				Column('password',  String(255), nullable=False, index=True),
				Column('comment',   Binary,      nullable=False, default=""),
				Column('time',	    DateTime,    nullable=False, index=True,
					onupdate = func.current_timestamp(),
					default = func.current_timestamp()),
				UniqueConstraint('username', 'game'),
				ForeignKeyConstraint(['game'], ['game.id']))

	def __str__(self):
		return "<User id=%s username=%s>" % (self.id, self.username)

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
