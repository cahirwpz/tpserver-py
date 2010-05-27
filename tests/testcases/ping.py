from common import ConnectedTestSession, Expect

class PingRequest( ConnectedTestSession ):
	""" Check if a server answers Ping packet properly. """

	def __iter__( self ):
		yield self.protocol.Ping( self.seq ), Expect( 'Okay' )

__tests__ = [ PingRequest ]
