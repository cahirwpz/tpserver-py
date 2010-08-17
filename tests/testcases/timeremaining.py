from test import TestSuite
from common import AuthorizedTestSession, Expect
from templates import WhenNotLogged

class GetTimeRemainingRequest( AuthorizedTestSession ):
	""" Checks if server responds to GetTimeRemaining request properly. """

	def __iter__( self ):
		GetTimeRemaining = self.protocol.use( 'GetTimeRemaining' )

		yield GetTimeRemaining( self.seq ), Expect( 'TimeRemaining' )

class GetTimeRemainingWhenNotLogged( WhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetTimeRemaining request? """

	__request__ = 'GetTimeRemaining'

	def makeRequest( self, GetTimeRemaining ):
		return GetTimeRemaining( self.seq )

class TimeRemainingTestSuite( TestSuite ):
	__name__  = 'TimeRemaining'
	__tests__ = [ GetTimeRemainingWhenNotLogged, GetTimeRemainingRequest ]

__tests__ = [ TimeRemainingTestSuite ]
