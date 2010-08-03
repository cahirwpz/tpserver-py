from common import AuthorizedTestSession, TestSuite

class GetObjectIds( AuthorizedTestSession ):
	""" Sends some random Object related requests. """

	def __iter__( self ):
		GetObjectIDs, GetObjectsByID = self.protocol.use( 'GetObjectIDs', 'GetObjectsByID' )

		response = yield GetObjectIDs( self.seq, -1, 0, 0, -1 )
		response = yield GetObjectIDs( self.seq, -1, 0, response.remaining, -1 )

		yield GetObjectsByID( self.seq, [ id for id, modtime in response.modtimes ] )

class ObjectTestSuite( TestSuite ):
	__name__ = 'Objects'

	def __init__( self ):
		TestSuite.__init__( self )

		self.addTest( GetObjectIds )

__tests__ = [ ObjectTestSuite ]
