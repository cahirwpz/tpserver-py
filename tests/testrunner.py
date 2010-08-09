#!/usr/bin/env python

from twisted.internet import reactor

from tp.server.gamemanager import GameManager
from tp.server.model import DatabaseManager

from test import TestLoader

class MainTestSuite( TestLoader ):#{{{
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

		Player = game.objects.use( 'Player' )

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

		with DatabaseManager().session() as session:
			session.add( player1 )
			session.add( player2 )

	def tearDown( self ):
		self.ctx['game'].reset()

	#def configure( self, configuration ):
	#	tests = configuration.tests
	#
	#	if tests == 'LIST':
	#		raise SystemExit( Logger.colorizeMessage( '\n'.join( self.__manager.getReport() ) ) )
	#	elif tests == 'DEFAULT':
	#		self.__tests = [ 'DEFAULT' ]
	#	elif tests == 'ALL':
	#		self.__tests = self.__manager.keys()
	#	else:
	#		for name in tests.split(','):
	#			try:
	#				names = fnmatch.filter( self.__manager.keys(), name )
	#
	#				if not names:
	#					raise KeyError( 'No test matching \'%s\'' % name )
	#
	#				self.__tests.extend( names )
	#			except KeyError, ex:
	#				raise SystemExit( ex )
	#
	#	if not self.__tests:
	#		raise ConfigurationError( 'test run is empty' )
#}}}

#class MainTestSuiteConfiguration( ComponentConfiguration ):#{{{
#	tests = StringOption( short='t', default='ALL',
#						  help='Specifies which tests will be added to test run. TEST-LIST is a list of test names or glob (see unix manual pages) patterns separated by comma. There are some arguments to this option that have a special meaning. \'LIST\' will force to display all available tests and finish the application. \'ALL\' will add all available test to test run.', arg_name='TEST-LIST' )
#}}}

class TestRunner( object ):#{{{
	def __init__( self ):
		self.suite = MainTestSuite()
		self.suite.result.addCallbacks( self.__succeeded, self.__failed )
	
	def __succeeded( self, test ):
		reactor.stop()
	
	def __failed( self, failure ):
		reactor.stop()

	def start( self ):
		reactor.callLater( 0, self.suite.start )
	
	def logPrefix( self ):
		return self.__class__.__name__
#}}}

__all__ = [ 'TestRunner' ]
