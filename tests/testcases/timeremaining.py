from common import Expect
from templates import AuthorizedTestSession, WhenNotLogged
from testenv import GameTestEnvMixin

class GetTimeRemainingRequest( AuthorizedTestSession, GameTestEnvMixin ):
	""" Checks if server responds to GetTimeRemaining request properly. """

	def __iter__( self ):
		GetTimeRemaining = self.protocol.use( 'GetTimeRemaining' )

		yield GetTimeRemaining( self.seq ), Expect( 'TimeRemaining' )

class GetTimeRemainingWhenNotLogged( WhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetTimeRemaining request? """

	__request__ = 'GetTimeRemaining'

	def makeRequest( self, GetTimeRemaining ):
		return GetTimeRemaining( self.seq )

__all__ = [	'GetTimeRemainingRequest', 
			'GetTimeRemainingWhenNotLogged' ]
