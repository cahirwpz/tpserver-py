from common import ConnectedTestSession, Expect

class GetFeaturesRequest( ConnectedTestSession ):
	""" Does server respond to GetFeatures request properly? """

	def __iter__( self ):
		GetFeatures = self.protocol.use( 'GetFeatures' )

		yield GetFeatures( self.seq ), Expect( 'Features' )

__tests__ = [ GetFeaturesRequest ]
