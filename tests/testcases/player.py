from test import TestSuite
from common import AuthorizedTestSession, Expect

class GetCurrentPlayer( AuthorizedTestSession ):
	""" Does server respond with current player information? """

	def setUp( self ):
		self.login		= self.ctx['players'][1].username
		self.password	= self.ctx['players'][1].password

	def __iter__( self ):
		player = self.ctx['players'][1]

		GetPlayer = self.protocol.use( 'GetPlayer' )

		packet = yield GetPlayer( self.seq, [0] ), Expect( 'Player' )

		if packet.id != player.id:
			self.failed( "Server responded with different PlayerId than requested!" )

class GetExistingPlayer( AuthorizedTestSession ):
	""" Does server respond properly if asked about existing player? """

	def __iter__( self ):
		player = self.ctx['players'][1]

		GetPlayer = self.protocol.use( 'GetPlayer' )

		packet = yield GetPlayer( self.seq, [ player.id ] ), Expect( 'Player' )

		if packet.id != player.id:
			self.failed( "Server responded with different PlayerId than requested!" )

class GetNonExistentPlayer( AuthorizedTestSession ):
	""" Does server fail to respond if asked about nonexistent player? """

	NoFailAllowed = False

	def __iter__( self ):
		player = self.ctx['players'][1]

		GetPlayer = self.protocol.use( 'GetPlayer' )

		packet = yield GetPlayer( self.seq, [ player.id + 666] ), Expect( 'Player', ('Fail', 'NoSuchThing') )

		if packet.type == 'Player':
			self.failed( "Server does return information for non-existent PlayerId = %s!" % ( player.id + 666 ) )

class GetMultiplePlayers( AuthorizedTestSession ):
	""" Does server return sequence of Player packets if asked about two players? """

	def __iter__( self ):
		player1 = self.ctx['players'][1]
		player2 = self.ctx['players'][0]

		GetPlayer = self.protocol.use( 'GetPlayer' )

		s, p1, p2 = yield GetPlayer( self.seq, [ player1.id, player2.id ] ), Expect( ('Sequence', 2, 'Player' ) )

		if p1.id != player1.id or p2.id != player2.id:
			self.failed( "Server returned different PlayerIds (%d,%d) than requested (%d,%d)." % (p1.id, p2.id, player1.id, player2.id) )

class PlayerTestSuite( TestSuite ):
	__name__  = 'Players'
	__tests__ = [ GetCurrentPlayer, GetExistingPlayer, GetNonExistentPlayer, GetMultiplePlayers ]

__tests__ = [ PlayerTestSuite ]
