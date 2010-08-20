#!/usr/bin/env python

from tp.server.gamemanager import GameManager
from tp.server.model import Model

class GameTestEnvMixin( object ):
	@property
	def model( self ):
		return self.game.model

	@property
	def sign_in_as( self ):
		return self.players[0]

	def setUp( self ):
		if 'test_minisecplus' not in GameManager():
			GameManager().addGame( 'test_minisecplus', 'Test Game (minisecplus)',
				'minisecplus', 'admin@localhost', 'Test game used for testing purposes')

		self.game = GameManager()[ 'test_minisecplus' ]

		Player = self.model.use( 'Player' )

		player1 = Player(
			username	= 'player1',
			password	= 'passwd1',
			email		= 'player1@localhost',
			comment		= 'Player used for testing purposes.' )

		player2 = Player(
			username	= 'player2',
			password	= 'passwd2',
			email		= 'player2@localhost',
			comment		= 'Player used for testing purposes.' )

		self.players = [ player1, player2 ]

		Model.add( self.players )

	def tearDown( self ):
		self.game.reset()

__all__ = [ 'GameTestEnvMixin' ]
