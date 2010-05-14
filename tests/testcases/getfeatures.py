from common import ConnectedTestSession

class CheckGetFeaturesRequest( ConnectedTestSession ):
	description = "Check if a server answers GetFeatures packet."

	def __iter__( self ):
		yield self.protocol.GetFeatures( self.seq )
