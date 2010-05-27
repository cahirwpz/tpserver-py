from common import AuthorizedTestSession

class GetObjectIds( AuthorizedTestSession ):
	""" Sends some random Object related requests. """

	def __iter__( self ):
		response = yield self.protocol.GetObjectIDs( self.seq, -1, 0, 0, -1 )
		response = yield self.protocol.GetObjectIDs( self.seq, -1, 0, response.remaining, -1 )
		yield self.protocol.GetObjectsByID( self.seq, [ id for id, modtime in response.modtimes ] )

__tests__ = [ GetObjectIds ]
