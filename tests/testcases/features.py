from test import TestSuite
from common import ConnectedTestSession, Expect

class GetFeaturesRequest( ConnectedTestSession ):
	""" Does server respond to GetFeatures request properly? """

	def __iter__( self ):
		GetFeatures = self.protocol.use( 'GetFeatures' )

		yield GetFeatures( self.seq ), Expect( 'Features' )

class FeaturesTestSuite( TestSuite ):
	__name__ = 'Features'

	def __init__( self ):
		super( FeaturesTestSuite, self ).__init__()

		self.addTest( GetFeaturesRequest )

__tests__ = [ FeaturesTestSuite ]
