from templates import ConnectedTestSession

class PingRequest( ConnectedTestSession ):
	""" Check if a server answers Ping packet properly. """

	def __iter__( self ):
		Ping = self.protocol.use( 'Ping' )

		response = yield Ping( self.seq )

		self.assertPacket( response, 'Okay' ) 

__all__ = [ 'PingRequest' ]
