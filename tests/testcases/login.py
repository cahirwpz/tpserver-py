from common import ConnectedTestSession, Expect, TestSuite

class KnownUserAuthorized( ConnectedTestSession ):
	""" Does server know a user that we know to exist? """

	Game		= "tp"
	Login		= "test"
	Password	= "test"

	def __iter__( self ):
		Login = self.protocol.use( 'Login' )

		yield Login( self.seq, "%s@%s" % ( self.Login, self.Game), self.Password ), Expect( 'Okay' )

class LoginTestSuite( TestSuite ):
	__name__ = 'Login'

	def __init__( self ):
		TestSuite.__init__( self )

		self.addTest( KnownUserAuthorized )

__tests__ = [ LoginTestSuite ]
