from test import TestSuite
from common import AuthorizedTestSession

class GetObjectIds( AuthorizedTestSession ):
	""" Sends some random Object related requests. """

	def __iter__( self ):
		GetObjectIDs, GetObjectsByID = self.protocol.use( 'GetObjectIDs', 'GetObjectsByID' )

		response = yield GetObjectIDs( self.seq, -1, 0, 0, -1 )
		response = yield GetObjectIDs( self.seq, -1, 0, response.remaining, -1 )

		yield GetObjectsByID( self.seq, [ id for id, modtime in response.modtimes ] )

class ObjectTestSuite( TestSuite ):
	__name__  = 'Objects'
	__tests__ = [ GetObjectIds ]

__tests__ = [ ObjectTestSuite ]
