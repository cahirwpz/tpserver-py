"""\
Resources require to build stuff.
"""
# Module imports
from sqlalchemy import *

# Local imports
from tp.server.bases.SQL import SQLBase, NoSuch

from tp.server.db import *
from tp.netlib import objects

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
		#Column('time',	    DateTime,    nullable=False, index=True, onupdate=func.current_timestamp()),
		Column('time',	    Integer,     nullable=False, index=True, onupdate=func.current_timestamp()),

		UniqueConstraint('shortname')
	)

	def __init__(self, id=None, packet=None, shortname=None, longname=None):
		if not (packet is None) or not (id is None):
			SQLBase.__init__(self, id=id, packet=packet)
		if not (shortname is None):
			SQLBase.__init__(self, id=self.gameid(shortname))
		if not (longname is None):
			SQLBase.__init__(self, id=self.gameid(self.munge(longname)))

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
		dbconn.use()
		t = Game.table
		try:
			return dbconn.execute(select([t.c.id], t.c.shortname==game)).fetchall()[0][0]
		except (KeyError, IndexError), e:
			raise NoSuch("No such game named %s exists!" % game)
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

