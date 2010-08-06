from test import TestSuite
from common import ConnectedTestSession, Expect

class GetTimeRemainingRequest( ConnectedTestSession ):
	""" Checks if server responds to GetTimeRemaining request properly. """

	def __iter__( self ):
		GetTimeRemaining = self.protocol.use( 'GetTimeRemaining' )

		yield GetTimeRemaining( self.seq ), Expect( 'TimeRemaining' )

class TimeRemainingTestSuite( TestSuite ):
	__name__  = 'TimeRemaining'
	__tests__ = [ GetTimeRemainingRequest ]

__tests__ = [ TimeRemainingTestSuite ]
