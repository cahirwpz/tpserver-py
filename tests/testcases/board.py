from common import AuthorizedTestSession, Expect

class GetCurrentBoard( AuthorizedTestSession ):
	""" Does server respond with current board information? """

	Login		= "test2"
	Password	= "test2"

	def __iter__( self ):
		packet = yield self.protocol.GetBoards( self.seq, [0] ), Expect( 'Board' )

		if packet.id != 2:
			self.failed( "Server responded with different BoardId than requested!" )

class GetExistingBoard( AuthorizedTestSession ):
	""" Does server respond properly if asked about existing board? """

	def __iter__( self ):
		packet = yield self.protocol.GetBoards( self.seq, [1] ), Expect( 'Board' )

		if packet.id != 1:
			self.failed( "Server responded with different BoardId than requested!" )

class GetNonExistentBoard( AuthorizedTestSession ):
	""" Does server fail to respond if asked about nonexistent board? """

	NoFailAllowed = False
	WrongBoardId = 666

	def __iter__( self ):
		packet = yield self.protocol.GetBoards( self.seq, [self.WrongBoardId] ), Expect( 'Board', ('Fail', 'NoSuchThing') )

		if packet.type == 'Board':
			self.failed( "Server does return information for non-existent BoardId = %s!" % self.WrongBoardId )

class GetMultipleBoards( AuthorizedTestSession ):
	""" Does server return sequence of Board packets if asked about two boards? """

	def __iter__( self ):
		s, p1, p2 = yield self.protocol.GetBoards( self.seq, [1, 2] ), Expect( ('Sequence', 2, 'Board' ) )

		if p1.id != 1 or p2.id != 2:
			self.failed( "Server returned different BoardIds (%d,%d) than requested (1,2)." % (p1.id, p2.id) )

__tests__ = [ GetExistingBoard, GetNonExistentBoard, GetCurrentBoard, GetMultipleBoards ]