from test import TestSuite
from common import AuthorizedTestSession, Expect, ExpectSequence, TestSessionUtils
from templates import GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged, GetItemWithID, GetItemsWithID

from tp.server.model import DatabaseManager

class GetBoardsMixin( TestSessionUtils ):#{{{
	__request__  = 'GetBoards'
	__response__ = 'Board'

	def assertEqual( self, packet, board ):
		for attr in [ 'id', 'name', 'description', 'messages', 'modtime' ]:
			pval = getattr( packet, attr, None )

			if attr == 'modtime':
				bval = self.datetimeToInt( board.mtime )
			elif attr == 'messages':
				bval = len( board.messages )
			else:
				bval = getattr( board, attr, None )

			assert pval == bval, \
					"Server responded with different %s.%s (%s) than expected (%s)!" % ( self.__response__, attr.title(), pval, bval )
#}}}

class GetCurrentBoard( GetItemWithID, GetBoardsMixin ):#{{{
	""" Does server respond with current board information? """

	@property
	def player( self ):
		return self.ctx['players'][1]

	@property
	def item( self ):
		return self.ctx['boards'][2]

	def getId( self, item ):
		return 0
#}}}

class GetExistingBoard( GetItemWithID, GetBoardsMixin ):#{{{
	""" Does server respond properly if asked about existing board? """

	@property
	def item( self ):
		return self.ctx['boards'][1]
#}}}

class GetNonExistentBoard( GetItemWithID, GetBoardsMixin ):#{{{
	""" Does server fail to respond if asked about nonexistent board? """

	__fail__ = 'NoSuchThing'

	@property
	def item( self ):
		return self.ctx['boards'][0]
	
	def getId( self, item ):
		return self.item.id + 666
#}}}

class GetPublicBoard( GetItemWithID, GetBoardsMixin ):#{{{
	""" Does server allow to fetch public Board? """

	@property
	def item( self ):
		return self.ctx['boards'][3]
#}}}

class GetPrivateBoard( GetItemWithID, GetBoardsMixin ):#{{{
	""" Does server allow to fetch private Board owned by the player? """

	@property
	def item( self ):
		return self.ctx['boards'][0]
#}}}

class GetOtherPlayerPrivateBoard( GetItemWithID, GetBoardsMixin ):#{{{
	""" Does server disallow to fetch private Board of another player? """

	__fail__ = 'PermissionDenied'

	@property
	def item( self ):
		return self.ctx['boards'][2]
#}}}

class GetMultipleBoards( GetItemsWithID, GetBoardsMixin ):#{{{
	""" Does server return sequence of Board packets if asked about two boards? """

	@property
	def items( self ):
		return [ self.ctx['boards'][1], self.ctx['boards'][0] ]
#}}}

class GetNumberOfBoards( AuthorizedTestSession ):#{{{
	""" Does server return the number of accessible Board IDs? """

	def __iter__( self ):
		GetBoardIDs = self.protocol.use( 'GetBoardIDs' )

		idseq = yield GetBoardIDs( self.seq, -1, 0, -1 ), Expect( 'BoardIDs' )

		assert idseq.remaining == 3, \
				"If requested the number of available IDs, then value of IDSequence.remaining should be 3 instead of %d" % idseq.remaining
		assert len( idseq.modtimes ) == 0, \
				"Expected to get no Boards"
#}}}

class GetAllAvailableBoards( AuthorizedTestSession, TestSessionUtils ):#{{{
	""" Does server return the IDs of Boards that are accessible by the player? """

	def __iter__( self ):
		GetBoardIDs = self.protocol.use( 'GetBoardIDs' )

		idseq = yield GetBoardIDs( self.seq, -1, 0, 3 ), Expect( 'BoardIDs' )

		assert len( idseq.modtimes ) == 3, \
				"Expected to get three Boards, got %s instead." % len( idseq.modtimes )

		cmpId = lambda a, b: cmp( a.id, b.id )

		boards = sorted( [self.ctx['boards'][0], self.ctx['boards'][1], self.ctx['boards'][3]], cmpId )

		for item, board in zip( sorted( idseq.modtimes, cmpId ), boards ):
			assert item.id == board.id, "Expected id (%s) and Board.id (%s) to be equal" % ( item.id )
			assert item.modtime == self.datetimeToInt( board.mtime ), "Expected modtime (%s) and Board.mtime (%s) to be equal." % ( item.modtime, board.mtime )
#}}}

class GetBoardWhenNotLogged( GetWithIDWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetBoards request? """

	__request__ = 'GetBoards'
#}}}

class GetBoardIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetBoardIds request? """

	__request__ = 'GetBoardIDs'
#}}}

class AllFetchedBoardsAreAccessible( AuthorizedTestSession ):#{{{
	""" Check if all fetched BoardIDs represent Boards that are accessible by the player. """

	@property
	def player( self ):
		return self.ctx['players'][1]

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
#}}}

class BoardAccessTestSuite( TestSuite ):#{{{
	""" Groups tests that check if access control for Board objects works properly. """
	__name__  = 'Access'
	__tests__ = [ GetCurrentBoard, AllFetchedBoardsAreAccessible,
			GetPublicBoard, GetPrivateBoard, GetOtherPlayerPrivateBoard ]
#}}}

class BoardTestSuite( TestSuite ):#{{{
	""" Performs all tests related to GetBoards and GetBoardIDs requests. """
	__name__  = 'Boards'
	__tests__ = [ GetBoardWhenNotLogged, GetBoardIDsWhenNotLogged,
			GetExistingBoard, GetNonExistentBoard, GetMultipleBoards,
			GetNumberOfBoards, GetAllAvailableBoards, BoardAccessTestSuite ]

	def setUp( self ):
		game = self.ctx['game']

		Board = game.objects.use( 'Board' )

		board1 = Board(
			owner       = self.ctx['players'][0],
			name        = "First message board for %s" % self.ctx['players'][0].username,
			description = "Board for testing purposes." )

		board2 = Board(
			owner       = self.ctx['players'][0],
			name        = "Second message board for %s" % self.ctx['players'][0].username,
			description = "Board for testing purposes." )

		board3 = Board(
			owner       = self.ctx['players'][1],
			name        = "Message board for %s" % self.ctx['players'][1].username,
			description = "Board for testing purposes." )

		board4 = Board(
			owner		= None,
			name		= "Public message board.",
			description = "Board for testing purposes." )

		self.ctx['boards'] = [ board1, board2, board3, board4 ]

		with DatabaseManager().session() as session:
			for board in self.ctx['boards']:
				session.add( board )
	
	def tearDown( self ):
		with DatabaseManager().session() as session:
			for board in self.ctx['boards']:
				board.remove( session )
#}}}

__tests__ = [ BoardTestSuite ]
