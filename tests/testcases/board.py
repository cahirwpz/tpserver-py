from common import ExpectSequence
from templates import ( AuthorizedTestSession, GetIDSequenceWhenNotLogged,
		GetWithIDWhenNotLogged, GetItemWithID, WithIDTestMixin, GetItemIDs,
		IDSequenceTestMixin )
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

class GetBoardsMixin( WithIDTestMixin ):
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
	def sign_in_as( self ):
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

	@property
	def item( self ):
		return self.boards[0]
	
	def getId( self, item ):
		return self.item.id + 666

	def getFail( self, item ):
		return 'NoSuchThing'

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

	@property
	def item( self ):
		return self.boards[2]

	def getFail( self, item ):
		return 'PermissionDenied'

class GetMultipleBoards( GetItemWithID, GetBoardsMixin, BoardTestEnvMixin ):
	""" Does server return sequence of Board packets if asked about two boards? """

	@property
	def items( self ):
		return [ self.boards[1], self.boards[0] ]

class GetMultipleBoardsWithOneFail( GetItemWithID, GetBoardsMixin, BoardTestEnvMixin ):
	""" Does server return sequence of Board packets if asked about two boards? """

	@property
	def items( self ):
		return [ self.boards[1], self.boards[2], self.boards[0] ]

	def getFail( self, item ):
		if item.owner not in [ None, self.sign_in_as ]:
			return 'PermissionDenied'

class GetNumberOfBoards( AuthorizedTestSession, BoardTestEnvMixin ):
	""" Does server return the number of accessible Board IDs? """

	def __iter__( self ):
		GetBoardIDs = self.protocol.use( 'GetBoardIDs' )

		idseq = yield GetBoardIDs( self.seq, -1, 0, -1 )

		self.assertPacket( idseq, 'BoardIDs' ) 

		self.assertEqual( idseq.remaining, 3,
				"If requested the number of available IDs, then value of IDSequence.remaining should be 3 instead of %d" % idseq.remaining )

		self.assertEqual( len( idseq.modtimes ), 0,
				"Expected to get no Boards" )

class GetAllAvailableBoardIDs( GetItemIDs, BoardTestEnvMixin ):
	""" Does server return the IDs of Boards that are accessible by the player? """

	__request__  = 'GetBoardIDs'
	__response__ = 'BoardIDs'

	@property
	def items( self ):
		return [ self.boards[0], self.boards[1], self.boards[3] ]

class GetBoardIDsOneByOne( AuthorizedTestSession, IDSequenceTestMixin, BoardTestEnvMixin ):
	""" Does server support IDSequence.key field properly? """

	def __iter__( self ):
		GetBoardIDs = self.protocol.use( 'GetBoardIDs' )

		idseq = yield GetBoardIDs( self.seq, -1, 0, 1 )

		self.assertPacket( idseq, 'BoardIDs' ) 
		self.assertIDSequenceEqual( idseq, [ self.boards[0] ], 2 )

		key = idseq.key

		idseq = yield GetBoardIDs( self.seq, key, 1, 1 )

		self.assertPacket( idseq, 'BoardIDs' ) 
		self.assertIDSequenceEqual( idseq, [ self.boards[1] ], 1 )

		idseq = yield GetBoardIDs( self.seq, key, 2, 1 )

		self.assertPacket( idseq, 'BoardIDs' ) 
		self.assertIDSequenceEqual( idseq, [ self.boards[3] ], 0 )

class GetBoardWhenNotLogged( GetWithIDWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetBoards request? """

	__request__ = 'GetBoards'

class GetBoardIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetBoardIds request? """

	__request__ = 'GetBoardIDs'

class AllFetchedBoardsAreAccessible( AuthorizedTestSession, IDSequenceTestMixin, GetBoardsMixin, BoardTestEnvMixin ):
	""" Check if all fetched BoardIDs represent Boards that are accessible by the player. """

	@property
	def sign_in_as( self ):
		return self.players[1]

	@property
	def items( self ):
		return [ self.boards[2], self.boards[3] ]

	def __iter__( self ):
		GetBoardIDs = self.protocol.use( 'GetBoardIDs' )

		idseq = yield GetBoardIDs( self.seq, -1, 0, 2 )

		self.assertPacket( idseq, 'BoardIDs' ) 
		self.assertIDSequenceEqual( idseq, self.items, 0 )

		GetBoards = self.protocol.use( 'GetBoards' )

		ids = [ id for id, modtime in idseq.modtimes ]

		response = yield GetBoards( self.seq, ids )

		self.assertPacketType( response, ExpectSequence( 2, 'Board' ) )
		self.assertPacketSeqEqual( response, self.items )

__all__ = [	'GetCurrentBoard', 
			'GetExistingBoard', 
			'GetNonExistentBoard', 
			'GetPublicBoard', 
			'GetPrivateBoard', 
			'GetOtherPlayerPrivateBoard', 
			'GetMultipleBoards', 
			'GetMultipleBoardsWithOneFail', 
			'GetNumberOfBoards', 
			'GetAllAvailableBoardIDs', 
			'GetBoardIDsOneByOne', 
			'GetBoardWhenNotLogged', 
			'GetBoardIDsWhenNotLogged', 
			'AllFetchedBoardsAreAccessible' ]
