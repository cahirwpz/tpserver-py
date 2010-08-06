from test import TestSuite
from common import AuthorizedTestSession, Expect

class GetCurrentPlayer( AuthorizedTestSession ):
	""" Does server respond with current player information? """

	def setUp( self ):
		self.login		= self.ctx['player2'].username
		self.password	= self.ctx['player2'].password

	def __iter__( self ):
		GetPlayer = self.protocol.use( 'GetPlayer' )

		packet = yield GetPlayer( self.seq, [0] ), Expect( 'Player' )

		if packet.id != 2:
			self.failed( "Server responded with different PlayerId than requested!" )

class GetExistingPlayer( AuthorizedTestSession ):
	""" Does server respond properly if asked about existing player? """

	def __iter__( self ):
		GetPlayer = self.protocol.use( 'GetPlayer' )

		packet = yield GetPlayer( self.seq, [1] ), Expect( 'Player' )

		if packet.id != 1:
			self.failed( "Server responded with different PlayerId than requested!" )

class GetNonExistentPlayer( AuthorizedTestSession ):
	""" Does server fail to respond if asked about nonexistent player? """

	NoFailAllowed = False
	WrongPlayerId = 666

	def __iter__( self ):
		GetPlayer = self.protocol.use( 'GetPlayer' )

		packet = yield GetPlayer( self.seq, [self.WrongPlayerId] ), Expect( 'Player', ('Fail', 'NoSuchThing') )

		if packet.type == 'Player':
			self.failed( "Server does return information for non-existent PlayerId = %s!" % self.WrongPlayerId )

class GetMultiplePlayers( AuthorizedTestSession ):
	""" Does server return sequence of Player packets if asked about two players? """

	def __iter__( self ):
		GetPlayer = self.protocol.use( 'GetPlayer' )

		s, p1, p2 = yield GetPlayer( self.seq, [1, 2] ), Expect( ('Sequence', 2, 'Player' ) )

		if p1.id != 1 or p2.id != 2:
			self.failed( "Server returned different PlayerIds (%d,%d) than requested (1,2)." % (p1.id, p2.id) )

class PlayerTestSuite( TestSuite ):
	__name__  = 'Players'
	__tests__ = [ GetCurrentPlayer, GetExistingPlayer, GetNonExistentPlayer, GetMultiplePlayers ]

__tests__ = [ PlayerTestSuite ]
