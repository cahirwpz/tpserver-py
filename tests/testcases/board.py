from test import TestSuite
from common import ( AuthorizedTestSession, Expect, TestSessionUtils,
		ConnectedTestSession, GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged )

from tp.server.model import DatabaseManager

class GetSingleBoard( AuthorizedTestSession ):#{{{
	def __iter__( self ):
		GetBoards = self.protocol.use( 'GetBoards' )

		packet = yield GetBoards( self.seq, [self.board.id] ), Expect( 'Board' )

		assert packet.id == self.board.id, \
				"Server responded with different BoardId (%s) than expected (%s)!" % ( packet.id, self.board.id )
#}}}

class GetCurrentBoard( AuthorizedTestSession ):#{{{
	""" Does server respond with current board information? """

	def setUp( self ):
		self.login = self.ctx['players'][1].username
		self.password = self.ctx['players'][1].password

	def __iter__( self ):
		board = self.ctx['boards'][2]

		GetBoards = self.protocol.use( 'GetBoards' )

		packet = yield GetBoards( self.seq, [0] ), Expect( 'Board' )

		assert packet.id == board.id, \
				"Server responded with different BoardId (%s) than expected (%s)!" % ( packet.id, board.id )
#}}}

class GetExistingBoard( GetSingleBoard ):#{{{
	""" Does server respond properly if asked about existing board? """

	def setUp( self ):
		self.board = self.ctx['boards'][1]
#}}}

class GetNonExistentBoard( AuthorizedTestSession ):#{{{
	""" Does server fail to respond if asked about nonexistent board? """

	def __iter__( self ):
		boardId = self.ctx['boards'][0].id + 666

		GetBoards = self.protocol.use( 'GetBoards' )

		packet = yield GetBoards( self.seq, [ boardId ] ), Expect( 'Board', ('Fail', 'NoSuchThing') )

		assert packet.type != 'Board', \
			"Server does return information for non-existent BoardId (%s)!" % boardId
#}}}

class GetMultipleBoards( AuthorizedTestSession ):#{{{
	""" Does server return sequence of Board packets if asked about two boards? """

	def __iter__( self ):
		b1 = self.ctx['boards'][1]
		b2 = self.ctx['boards'][0]

		GetBoards = self.protocol.use( 'GetBoards' )

		s, p1, p2 = yield GetBoards( self.seq, [ b1.id, b2.id ] ), Expect( ('Sequence', 2, 'Board' ) )

		assert p1.id == b1.id and p2.id == b2.id, \
				"Server returned different BoardIds (%d,%d) than requested (%d,%d)." % ( p1.id, p2.id, b1.id, b2.id )
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

class GetPublicBoard( GetSingleBoard ):#{{{
	""" Does server allow to fetch public Board? """

	def setUp( self ):
		self.board = self.ctx['boards'][3]
#}}}

class GetPrivateBoard( GetSingleBoard ):#{{{
	""" Does server allow to fetch private Board owned by the player? """

	def setUp( self ):
		self.board = self.ctx['boards'][0]
#}}}

class GetOtherPlayerPrivateBoard( AuthorizedTestSession ):#{{{
	""" Does server disallow to fetch private Board of another player? """

	def __iter__( self ):
		board = self.ctx['boards'][2]

		GetBoards = self.protocol.use( 'GetBoards' )

		packet = yield GetBoards( self.seq, [ board.id ] ), Expect( 'Board', ('Fail', 'PermissionDenied') )

		assert packet.type != 'Board', \
			"Server does allow to access a private Board of another player!"
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

	def setUp( self ):
		self.login = self.ctx['players'][1].username
		self.password = self.ctx['players'][1].password

	def __iter__( self ):
		GetBoardIDs = self.protocol.use( 'GetBoardIDs' )

		idseq = yield GetBoardIDs( self.seq, -1, 0, 2 ), Expect( 'BoardIDs' )

		assert len( idseq.modtimes ) == 2, \
				"Expected to get three Boards, got %s instead." % len( idseq.modtimes )

		GetBoards = self.protocol.use( 'GetBoards' )

		ids = [ id for id, modtime in idseq.modtimes ]

		s, p1, p2 = yield GetBoards( self.seq, ids ), Expect( ('Sequence', 2, 'Board' ) )

		assert p1.id == ids[0] and p2.id == ids[1], \
				"Server returned different BoardIds (%d,%d) than expected (%d,%d)." % ( p1.id, p2.id, ids[0], ids[1] )
#}}}

class BoardTestSuite( TestSuite ):#{{{
	""" Performs all tests related to GetBoards and GetBoardIDs requests. """
	__name__  = 'Boards'
	__tests__ = [ GetBoardWhenNotLogged, GetBoardIDsWhenNotLogged,
			GetExistingBoard, GetNonExistentBoard, GetCurrentBoard,
			GetMultipleBoards, GetNumberOfBoards, GetAllAvailableBoards,
			AllFetchedBoardsAreAccessible, GetPublicBoard, GetPrivateBoard,
			GetOtherPlayerPrivateBoard ]

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
