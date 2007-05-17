"""\
Resources require to build stuff.
"""
# Module imports
from sqlalchemy import *

# Local imports
from tp.server.db import dbconn
from tp import netlib
from SQL import SQLBase

class Game(SQLBase):
	table = Table('game',
		Column('id',	    Integer,     nullable=False, index=True, primary_key=True),
		Column('rulesetname', String(255), nullable=False, index=True),       # Ruleset this game uses
		Column('shortname', String(255), nullable=False, index=True),       # Computer name
		Column('longname',  Binary,      nullable=False, default=""), 		# Human readable name
		Column('admin',     String(255), nullable=False, index=True), 		# Admin's email address
		Column('comment',   Binary,      nullable=False, default=""), 		# A generic comment
		Column('turn',	    Integer,     nullable=False), 					# The current turn of the game
		Column('commandline', Binary,    nullable=False), 					# The command line used to create the game

		UniqueConstraint('shortname')
	)

	def munge(game):
		"""\
		Convert a longname into some sort of suitable short name.
		"""
		return game.replace(' ', '').strip().lower()
	munge = staticmethod(munge)

	def gameid(game):
		"""\
		Get the id of a game from a short name.
		"""
		t = Game.table
		try:
			result = dbconn.execute(select([t.c.id], t.c.shortname==game)).fetchall()[0]
		except (KeyError, IndexError), e:
			raise KeyError("No such game named %s exists!" % game)
	gameid = staticmethod(gameid)

	def ruleset_get(self):
		"""\
		Return the Ruleset this game uses.
		""" 
		try:
			return self.__ruleset
		except AttributeError:
			exec("from tp.server.rules.%s import Ruleset" % self.rulesetname)
			self.__ruleset = Ruleset(self)
			return self.__ruleset

	def ruleset_set(self, value):
		if hasattr(self, 'rulesetname'):
			raise TypeError('A ruleset can only be set once!')
		try:
			exec("from tp.server.rules.%s import Ruleset" % value)
		except ImportError:	
			raise ImportError("This game references a ruleset which doesn't exist anymore! Please reinstall the ruleset.")
		self.rulesetname = value

	ruleset = property(ruleset_get, ruleset_set)
	

	def to_packet(self, sequence):
		# Preset arguments
		args = [sequence, self.id, self.username, ""]
		return netlib.objects.Player(*args)

