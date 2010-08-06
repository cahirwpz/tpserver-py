from test import TestSuite
from common import ConnectedTestSession, Expect

class KnownUserAuthorized( ConnectedTestSession ):
	""" Does server know a user that we know to exist? """

	def setUp( self ):
		self.game		= self.ctx['game'].name
		self.login		= self.ctx['player1'].username
		self.password	= self.ctx['player1'].password

	def __iter__( self ):
		Login = self.protocol.use( 'Login' )

		yield Login( self.seq, "%s@%s" % ( self.login, self.game ), self.password ), Expect( 'Okay' )

class LoginTestSuite( TestSuite ):
	__name__  = 'Login'
	__tests__ = [ KnownUserAuthorized ]

__tests__ = [ LoginTestSuite ]
