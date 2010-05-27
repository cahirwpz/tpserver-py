from common import AuthorizedTestSession, Expect

class GetCurrentPlayer( AuthorizedTestSession ):
	""" Does server respond with current player information? """

	Login		= "test2"
	Password	= "test2"

	def __iter__( self ):
		packet = yield self.protocol.GetPlayer( self.seq, [0] ), Expect( 'Player' )

		if packet.id != 2:
			self.failed( "Server responded with different PlayerId than requested!" )

class GetExistentPlayer( AuthorizedTestSession ):
	""" Does server respond properly if asked about existent player? """

	def __iter__( self ):
		packet = yield self.protocol.GetPlayer( self.seq, [1] ), Expect( 'Player' )

		if packet.id != 1:
			self.failed( "Server responded with different PlayerId than requested!" )

class GetNonExistentPlayer( AuthorizedTestSession ):
	""" Does server fail to respond if asked about nonexistent player? """

	NoFailAllowed = False
	WrongPlayerId = 666

	def __iter__( self ):
		packet = yield self.protocol.GetPlayer( self.seq, [self.WrongPlayerId] ), Expect( 'Player', ('Fail', 'NoSuchThing') )

		if packet.type == 'Player':
			self.failed( "Server does return information for non-existent PlayerId = %s!" % self.WrongPlayerId )

class GetMultiplePlayers( AuthorizedTestSession ):
	""" Does server return sequence of Player packets if asked about two players? """

	def __iter__( self ):
		s, p1, p2 = yield self.protocol.GetPlayer( self.seq, [1, 2] ), Expect( ('Sequence', 2, 'Player' ) )

		if p1.id != 1 or p2.id != 2:
			self.failed( "Server returned different PlayerIds (%d,%d) than requested (1,2)." % (p1.id, p2.id) )

__tests__ = [ GetCurrentPlayer, GetExistentPlayer, GetNonExistentPlayer, GetMultiplePlayers ]
