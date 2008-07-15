"""\
Resources require to build stuff.
"""
# Module imports
from sqlalchemy import *

# Local imports
from tp.server.db   import *
from tp.server.bases.Game import Game

from tp import netlib
from SQL import SQLBase

class User(SQLBase):
	table = Table('user', metadata,
		Column('game', 	    Integer,     nullable=False, index=True, primary_key=True),
		Column('id',	    Integer,     nullable=False, index=True, primary_key=True),
		Column('username',  String(255), nullable=False, index=True),
		Column('password',  String(255), nullable=False, index=True),
		Column('comment',   Binary,      nullable=False, default=""),
		Column('done', 	    Boolean,     nullable=False, default=False),
		Column('time',	    DateTime,    nullable=False, index=True,
			onupdate=func.current_timestamp(), default=func.current_timestamp()),

		UniqueConstraint('username', 'game'),
		ForeignKeyConstraint(['game'], ['game.id']),
	)

	@staticmethod
	def usernameid(game, username, password=None):
		"""\
		Get the id for a user given a game, username and password.
		"""
		dbconn.use(game)

		t = User.table
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
		"""\
		Split a username into the user and game parts.
		"""
		if username.find('@') == -1:
			raise TypeError('The given username is not valid...')
		
		return username.split('@', 1)

	@classmethod
	def realid(cls, user, pid):
		if pid == 0:
			return user.id
		return pid

	def __str__(self):
		return "<User id=%s username=%s>" % (self.id, self.username)

	def game_get(self):
		return self.__game.id
	def game_set(self, value):
		if hasattr(self, '__game'):
			raise TypeError('The game can not be changed!')
		self.__game = Game(id=value)
	game = property(game_get, game_set)

	def playing(self):
		return self.__game
	playing = property(playing)

	def to_packet(self, user, sequence):
		# Preset arguments
		args = [sequence, self.id, self.username, ""]
		return netlib.objects.Player(*args)

