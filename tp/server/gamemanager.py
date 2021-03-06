#!/usr/bin/env

from collections import Mapping
from logging import info 

from tp.server.model import Model, Game as GameDesc
from tp.server.singleton import SingletonContainerClass
from tp.server.rules import RulesetManager

class Game( object ):
	def __init__( self, gamedesc ):
		self.__game  = gamedesc
		self.__model = Model( self )
		self.__ruleset = None

	@property
	def model( self ):
		return self.__model

	@property
	def name( self ):
		return self.__game.name

	@property
	def ruleset_name( self ):
		return self.__game.ruleset_name

	@property
	def turn( self ):
		return self.__game.turn
	
	def initialise( self ):
		Model.add( self.__game )

		self.ruleset.loadModelConstants()
		self.ruleset.initModelConstants()
		self.ruleset.loadModel()
		self.ruleset.initModel()

		info( "Game '%s' initialised successfully.", self.name )

	def load( self ):
		self.ruleset.loadModelConstants()
		self.ruleset.loadModel()

		info( "Game '%s' loaded successfully.", self.name )
	
	def remove( self ):
		Model.drop( self.__game.model )
		Model.remove( self.__game )

	def reset( self ):
		self.ruleset.resetModel()
	
	@property
	def ruleset( self ):
		"""
		Return the Ruleset (object) this game uses.
		""" 
		if self.__ruleset is None:
			self.__ruleset = RulesetManager()[ self.ruleset_name ]( self )

		return self.__ruleset

	@ruleset.setter
	def ruleset( self, name ):
		self.__ruleset = RulesetManager()[ name ]( self )

		self.ruleset_name = name

class GameManager( Mapping ):
	__metaclass__ = SingletonContainerClass

	def __init__( self ):
		Model.init()

		self.__game = {}

		for gamedesc in GameDesc.query().all():
			game = Game( gamedesc )
			game.load()

			self.__game[ game.name ] = game
	
	def __getitem__( self, name ):
		return self.__game[ name ]

	def __iter__( self ):
		return self.__game.__iter__()

	def __len__( self ):
		return self.__game.__len__()

	def addGame( self, name, longname, rulesetname, admin, comment ):
		game = self.__game.get( name, None )

		if not game:
			gamedesc = GameDesc( ruleset_name = rulesetname, name = name, longname = longname, admin = admin, comment = comment )

			game = Game( gamedesc )
			game.initialise()

			self.__game[ name ] = game

			info( "Game '%s' added successfully.", name )
		else:
			raise KeyError( "Game '%s' already exists!" % name )
	
	def removeGame( self, name ):
		game = self.__game.get( name, None )

		if game:
			game.remove()

			del self.__game[ name ]

			info( "Game '%s' removed successfully.", name )
		else:
			raise KeyError( "Game '%s' does not exists!" % name )
		
__all__ = [ 'GameManager', 'Game' ]
