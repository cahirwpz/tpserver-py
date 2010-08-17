from test import TestSuite
from common import AuthorizedTestSession, Expect, ExpectFail, ExpectSequence, ExpectOneOf
from templates import GetWithIDWhenNotLogged

class GetCurrentPlayer( AuthorizedTestSession ):
	""" Does server respond with current player information? """

	@property
	def player( self ):
		return self.ctx['players'][1]

	def __iter__( self ):
		GetPlayer = self.protocol.use( 'GetPlayer' )

		packet = yield GetPlayer( self.seq, [0] ), Expect( 'Player' )

		assert packet.id == self.player.id, \
			"Server responded with different PlayerId than requested!"

class GetExistingPlayer( AuthorizedTestSession ):
	""" Does server respond properly if asked about existing player? """

	def __iter__( self ):
		player = self.ctx['players'][1]

		GetPlayer = self.protocol.use( 'GetPlayer' )

		packet = yield GetPlayer( self.seq, [ player.id ] ), Expect( 'Player' )

		assert packet.id == player.id, \
			"Server responded with different PlayerId than requested!"

class GetNonExistentPlayer( AuthorizedTestSession ):
	""" Does server fail to respond if asked about nonexistent player? """

	def __iter__( self ):
		player = self.ctx['players'][1]

		GetPlayer = self.protocol.use( 'GetPlayer' )

		packet = yield GetPlayer( self.seq, [ player.id + 666] ), ExpectOneOf( 'Player', ExpectFail('NoSuchThing') )

		assert packet.type != 'Player', \
			"Server does return information for non-existent PlayerId = %s!" % ( player.id + 666 )

class GetMultiplePlayers( AuthorizedTestSession ):
	""" Does server return sequence of Player packets if asked about two players? """

	def __iter__( self ):
		player1 = self.ctx['players'][1]
		player2 = self.ctx['players'][0]

		GetPlayer = self.protocol.use( 'GetPlayer' )

		s, p1, p2 = yield GetPlayer( self.seq, [ player1.id, player2.id ] ), ExpectSequence(2, 'Player')

		assert p1.id == player1.id and p2.id == player2.id, \
			"Server returned different PlayerIds (%d,%d) than requested (%d,%d)." % (p1.id, p2.id, player1.id, player2.id)

class GetPlayerWhenNotLogged( GetWithIDWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetPlayers request? """

	__request__ = 'GetPlayer'

class PlayerTestSuite( TestSuite ):
	__name__  = 'Players'
	__tests__ = [ GetPlayerWhenNotLogged, GetCurrentPlayer, GetExistingPlayer, GetNonExistentPlayer, GetMultiplePlayers ]

__tests__ = [ PlayerTestSuite ]
