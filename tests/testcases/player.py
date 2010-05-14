from common import ConnectedTestSession

class CheckGetPlayerRequest( ConnectedTestSession ):
	description = "Checks if server responds to GetPlayer command properly."

	def __iter__( self ):
		response = yield self.protocol.GetPlayer( self.seq, [0] )
		#yield self.protocol.Player( 17, [ id for id, modtime in response.modtimes ] )
