from common import ConnectedTestSession, Expect

class KnownUserAuthorized( ConnectedTestSession ):
	""" Does server know a user that we know to exist? """

	Game		= "tp"
	Login		= "test"
	Password	= "test"

	def __iter__( self ):
		Login = self.protocol.use( 'Login' )

		yield Login( self.seq, "%s@%s" % ( self.Login, self.Game), self.Password ), Expect( 'Okay' )

__tests__ = [ KnownUserAuthorized ]
