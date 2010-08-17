#!/usr/bin/env python

from twisted.internet import reactor

from configuration import ComponentConfiguration, StringOption

from tp.server.gamemanager import GameManager
from tp.server.model import Model
from tp.server.logging import Logger

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

class TestRunner( object ):
	def __init__( self ):
		self.suite = MainTestSuite()
		self.suite.result.addCallbacks( self.__succeeded, self.__failed )
	
	def __succeeded( self, test ):
		reactor.stop()
	
	def __failed( self, failure ):
		reactor.stop()

	def start( self ):
		reactor.callLater( 0, lambda: self.suite.start( self.test_path ) )

	def configure( self, configuration ):
		tests = configuration.tests
	
		if tests == 'list':
			raise SystemExit( Logger.colorizeMessage( '\n'.join( self.suite.getListing() ) ) )
		else:
			self.test_path = tests
	
	def logPrefix( self ):
		return self.__class__.__name__

class TestRunnerConfiguration( ComponentConfiguration ):
	tests = StringOption( short='t', default='*',
						  help='Specifies which tests will be run. TEST-PATH is a test path using glob (see unix manual pages) pattern. If you provide \'list\' path then all available tests will be displayed and the application will finish.', arg_name='TEST-PATH' )

__all__ = [ 'TestRunner', 'TestRunnerConfiguration' ]
