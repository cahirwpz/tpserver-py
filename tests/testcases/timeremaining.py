from common import ConnectedTestSession

class CheckGetTimeRemainingRequest( ConnectedTestSession ):
	description = "Checks if server responds to GetTimeRemaining request properly."

	def __iter__( self ):
		yield self.protocol.GetTimeRemaining( self.seq )
