from common import ConnectedTestSession, Expect

class GetTimeRemainingRequest( ConnectedTestSession ):
	""" Checks if server responds to GetTimeRemaining request properly. """

	def __iter__( self ):
		yield self.protocol.GetTimeRemaining( self.seq ), Expect( 'TimeRemaining' )

__tests__ = [ GetTimeRemainingRequest ]
