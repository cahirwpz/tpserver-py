from common import ConnectedTestSession

class PingRequest( ConnectedTestSession ):
	""" Check if a server answers Ping packet properly. """

	def __iter__( self ):
		yield self.protocol.Ping( self.seq )

__tests__ = [ PingRequest ]
