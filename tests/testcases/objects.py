from common import AuthorizedTestSession

class CheckGetObjectIds( AuthorizedTestSession ):
	description = "Sends some random Object related requests."

	def __iter__( self ):
		response = yield self.protocol.GetObjectIDs( self.seq, -1, 0, 0 )
		response = yield self.protocol.GetObjectIDs( self.seq, -1, 0, response.remaining )
		yield self.protocol.GetObjectsByID( self.seq, [ id for id, modtime in response.modtimes ] )

		response = yield self.protocol.GetBoardIDs( self.seq, -1, 0, 0 )
		response = yield self.protocol.GetBoardIDs( self.seq, -1, 0, response.remaining )
		yield self.protocol.GetBoards( self.seq, [ id for id, modtime in response.modtimes ] )
