from test import TestSuite
from common import ConnectedTestSession, Expect
from testenv import GameTestEnvMixin

class KnownUserAuthorized( ConnectedTestSession, GameTestEnvMixin ):
	""" Does server know a user that we know to exist? """

	def setUp( self ):
		self.login		= self.players[0].username
		self.password	= self.players[0].password

	def __iter__( self ):
		Login = self.protocol.use( 'Login' )

		yield Login( self.seq, "%s@%s" % ( self.login, self.game.name ), self.password ), Expect( 'Okay' )

class LoginTestSuite( TestSuite ):
	__name__  = 'Login'
	__tests__ = [ KnownUserAuthorized ]

__tests__ = [ LoginTestSuite ]
