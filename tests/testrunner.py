#!/usr/bin/env python

from tp.server.gamemanager import GameManager
from tp.server.model import Model

from test import TestLoader

class MainTestSuite( TestLoader ):
	__testpath__ = [ 'Tests' ]
	__name__ = 'Tests'
	__path__ = 'testcases'

	def setUp( self ):
		if 'test_minisecplus' not in GameManager():
			GameManager().addGame( 'test_minisecplus', 'Test Game (minisecplus)',
				'minisecplus', 'admin@localhost', 'Test game used for testing purposes')

		game = GameManager()[ 'test_minisecplus' ]
		game.reset()

		self.ctx['game'] = game

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

		self.ctx['players']	= [ player1, player2 ]

		Model.add( player1, player2 )

__all__ = [ 'MainTestSuite' ]
