from common import ConnectedTestSession, Expect

class PingRequest( ConnectedTestSession ):
	""" Check if a server answers Ping packet properly. """

	def __iter__( self ):
		Ping = self.protocol.use( 'Ping' )

		yield Ping( self.seq ), Expect( 'Okay' )
