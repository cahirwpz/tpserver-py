from common import ConnectedTestSession

class CheckPingPacketRequest( ConnectedTestSession ):
	name = "Check if a server answers Ping packet properly."

	def __iter__( self ):
		yield self.protocol.Ping( self.seq )
