from common import ConnectedTestSession, Expect, TestSuite

class GetTimeRemainingRequest( ConnectedTestSession ):
	""" Checks if server responds to GetTimeRemaining request properly. """

	def __iter__( self ):
		GetTimeRemaining = self.protocol.use( 'GetTimeRemaining' )

		yield GetTimeRemaining( self.seq ), Expect( 'TimeRemaining' )

class TimeRemainingTestSuite( TestSuite ):
	__name__ = 'TimeRemaining'

	def __init__( self ):
		TestSuite.__init__( self )

		self.addTest( GetTimeRemainingRequest )

__tests__ = [ TimeRemainingTestSuite ]
