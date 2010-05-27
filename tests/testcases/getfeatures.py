from common import ConnectedTestSession, Expect

class GetFeaturesRequest( ConnectedTestSession ):
	""" Does server respond to GetFeatures request properly? """

	def __iter__( self ):
		yield self.protocol.GetFeatures( self.seq ), Expect( 'Features' )

__tests__ = [ GetFeaturesRequest ]
