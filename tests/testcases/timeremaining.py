from common import ConnectedTestSession

class GetTimeRemainingRequest( ConnectedTestSession ):
	""" Checks if server responds to GetTimeRemaining request properly. """

	def __iter__( self ):
		yield self.protocol.GetTimeRemaining( self.seq )

__tests__ = [ GetTimeRemainingRequest ]
