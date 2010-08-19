from common import AuthorizedTestSession, Expect, ExpectSequence, TestSessionUtils
from templates import GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged, GetItemWithID, GetItemsWithID, GetWithIDMixin
from testenv import GameTestEnvMixin

from tp.server.model import Model

class BoardTestEnvMixin( GameTestEnvMixin ):
	def setUp( self ):
		Board = self.model.use( 'Board' )

		board1 = Board(
			owner       = self.players[0],
			name        = "First message board for %s" % self.players[0].username,
			description = "Board for testing purposes." )

		board2 = Board(
			owner       = self.players[0],
			name        = "Second message board for %s" % self.players[0].username,
			description = "Board for testing purposes." )

		board3 = Board(
			owner       = self.players[1],
			name        = "Message board for %s" % self.players[1].username,
			description = "Board for testing purposes." )

		board4 = Board(
			owner		= None,
			name		= "Public message board.",
			description = "Board for testing purposes." )

		self.boards = [ board1, board2, board3, board4 ]

		Model.add( self.boards )

	def tearDown( self ):
		Model.remove( self.boards )

class GetBoardsMixin( GetWithIDMixin ):
	__request__  = 'GetBoards'
	__response__ = 'Board'

	__attrs__   = [ 'id', 'name', 'description' ]
	__attrmap__ = {}
	__attrfun__ = [ 'modtime', 'messages' ]

	def convert_messages( self, packet, obj ):
		return packet.messages, len( obj.messages )

class GetCurrentBoard( GetItemWithID, GetBoardsMixin, BoardTestEnvMixin ):
	""" Does server respond with current board information? """

	@property
	def player( self ):
		return self.players[1]

	@property
	def item( self ):
		return self.boards[2]

	def getId( self, item ):
		return 0

class GetExistingBoard( GetItemWithID, GetBoardsMixin, BoardTestEnvMixin ):
	""" Does server respond properly if asked about existing board? """

	@property
	def item( self ):
		return self.boards[1]

class GetNonExistentBoard( GetItemWithID, GetBoardsMixin, BoardTestEnvMixin ):
	""" Does server fail to respond if asked about nonexistent board? """

	__fail__ = 'NoSuchThing'

	@property
	def item( self ):
		return self.boards[0]
	
	def getId( self, item ):
		return self.item.id + 666

class GetPublicBoard( GetItemWithID, GetBoardsMixin, BoardTestEnvMixin ):
	""" Does server allow to fetch public Board? """

	@property
	def item( self ):
		return self.boards[3]

class GetPrivateBoard( GetItemWithID, GetBoardsMixin, BoardTestEnvMixin ):
	""" Does server allow to fetch private Board owned by the player? """

	@property
	def item( self ):
		return self.boards[0]

class GetOtherPlayerPrivateBoard( GetItemWithID, GetBoardsMixin, BoardTestEnvMixin ):
	""" Does server disallow to fetch private Board of another player? """

	__fail__ = 'PermissionDenied'

	@property
	def item( self ):
		return self.boards[2]

class GetMultipleBoards( GetItemsWithID, GetBoardsMixin, BoardTestEnvMixin ):
	""" Does server return sequence of Board packets if asked about two boards? """

	@property
	def items( self ):
		return [ self.boards[1], self.boards[0] ]

class GetMultipleBoardsWithOneFail( GetItemsWithID, GetBoardsMixin, BoardTestEnvMixin ):
	""" Does server return sequence of Board packets if asked about two boards? """

	@property
	def items( self ):
		return [ self.boards[1], self.boards[2], self.boards[0] ]

	def getFail( self, item ):
		if item.owner not in [ None, self.player ]:
			return 'PermissionDenied'

class GetNumberOfBoards( AuthorizedTestSession, BoardTestEnvMixin ):
	""" Does server return the number of accessible Board IDs? """

	def __iter__( self ):
		GetBoardIDs = self.protocol.use( 'GetBoardIDs' )

		idseq = yield GetBoardIDs( self.seq, -1, 0, -1 ), Expect( 'BoardIDs' )

		assert idseq.remaining == 3, \
				"If requested the number of available IDs, then value of IDSequence.remaining should be 3 instead of %d" % idseq.remaining
		assert len( idseq.modtimes ) == 0, \
				"Expected to get no Boards"

class GetAllAvailableBoards( AuthorizedTestSession, TestSessionUtils, BoardTestEnvMixin ):
	""" Does server return the IDs of Boards that are accessible by the player? """

	def __iter__( self ):
		GetBoardIDs = self.protocol.use( 'GetBoardIDs' )

		idseq = yield GetBoardIDs( self.seq, -1, 0, 3 ), Expect( 'BoardIDs' )

		assert len( idseq.modtimes ) == 3, \
				"Expected to get three Boards, got %s instead." % len( idseq.modtimes )

		cmpId = lambda a, b: cmp( a.id, b.id )

		boards = sorted( [self.boards[0], self.boards[1], self.boards[3]], cmpId )

		for item, board in zip( sorted( idseq.modtimes, cmpId ), boards ):
			assert item.id == board.id, "Expected id (%s) and Board.id (%s) to be equal" % ( item.id )
			assert item.modtime == self.datetimeToInt( board.mtime ), "Expected modtime (%s) and Board.mtime (%s) to be equal." % ( item.modtime, board.mtime )

class GetBoardIDsOneByOne( AuthorizedTestSession, BoardTestEnvMixin ):
	""" Does server support IDSequence.key field properly? """

	def __iter__( self ):
		GetBoardIDs = self.protocol.use( 'GetBoardIDs' )

		idseq = yield GetBoardIDs( self.seq, -1, 0, 1 ), Expect( 'BoardIDs' )

		key = idseq.key

		assert idseq.remaining == 2, \
				"There should be two Boards left."

		idseq = yield GetBoardIDs( self.seq, key, 1, 1 ), Expect( 'BoardIDs' )

		assert idseq.remaining == 1, \
				"There should be one Board left."

		idseq = yield GetBoardIDs( self.seq, key, 2, 1 ), Expect( 'BoardIDs' )

		assert idseq.remaining == 0, \
				"There should be no Board left."

class GetBoardWhenNotLogged( GetWithIDWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetBoards request? """

	__request__ = 'GetBoards'

class GetBoardIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetBoardIds request? """

	__request__ = 'GetBoardIDs'

class AllFetchedBoardsAreAccessible( AuthorizedTestSession, BoardTestEnvMixin ):
	""" Check if all fetched BoardIDs represent Boards that are accessible by the player. """

	@property
	def player( self ):
		return self.players[1]

	def __iter__( self ):
		GetBoardIDs = self.protocol.use( 'GetBoardIDs' )

		idseq = yield GetBoardIDs( self.seq, -1, 0, 2 ), Expect( 'BoardIDs' )

		assert len( idseq.modtimes ) == 2, \
				"Expected to get two Boards, got %s instead." % len( idseq.modtimes )

		assert idseq.remaining == 0, \
				"Database should contain exactly two Boards for the player."

		GetBoards = self.protocol.use( 'GetBoards' )

		ids = [ id for id, modtime in idseq.modtimes ]

		s, p1, p2 = yield GetBoards( self.seq, ids ), ExpectSequence(2, 'Board')

		assert p1.id == ids[0] and p2.id == ids[1], \
				"Server returned different BoardIds (%d,%d) than expected (%d,%d)." % ( p1.id, p2.id, ids[0], ids[1] )

__all__ = [	'GetCurrentBoard', 
			'GetExistingBoard', 
			'GetNonExistentBoard', 
			'GetPublicBoard', 
			'GetPrivateBoard', 
			'GetOtherPlayerPrivateBoard', 
			'GetMultipleBoards', 
			'GetMultipleBoardsWithOneFail', 
			'GetNumberOfBoards', 
			'GetAllAvailableBoards', 
			'GetBoardIDsOneByOne', 
			'GetBoardWhenNotLogged', 
			'GetBoardIDsWhenNotLogged', 
			'AllFetchedBoardsAreAccessible' ]
