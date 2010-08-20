from common import TestSession

class SameSequenceInHeader( TestSession ):
	""" Checks if a server drops second packet with same sequence. """

	def __iter__( self ):
		Connect, Ping = self.protocol.use( 'Connect', 'Ping' )

		packet = yield Connect( 1, "tpserver-tests client" )

		self.assertPacket( packet, 'Okay' )

		packet = yield Ping( 2 )

		self.assertPacket( packet, 'Okay' )

		packet = yield Ping( 2 )

		self.assertPacketFail( packet, 'Frame',
				"Server does accept multiple packets with same sequence number!" )

__all__ = [ 'SameSequenceInHeader' ]
