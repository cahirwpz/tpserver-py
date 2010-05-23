from common import ConnectedTestSession

class GetFeaturesRequest( ConnectedTestSession ):
	""" Check if a server answers GetFeatures packet. """

	def __iter__( self ):
		yield self.protocol.GetFeatures( self.seq )

__tests__ = [ GetFeaturesRequest ]
