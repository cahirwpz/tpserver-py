from templates import ConnectedTestSession

class GetFeaturesRequest( ConnectedTestSession ):
	""" Does server respond to GetFeatures request properly? """

	def __iter__( self ):
		GetFeatures = self.protocol.use( 'GetFeatures' )

		response = yield GetFeatures( self.seq )

		self.assertPacket( response, 'Features' ) 

__all__ = [ 'GetFeaturesRequest' ]
